from . import LA_CONSTANTS
from . import LA_XISNAN

@bind("CBBCSD")
@external
def cbbcsd(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    JOBV2T: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    U1: Complex64[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Complex64[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Complex64[LDV1T, Flat],
    LDV1T: Addr(Int32),
    V2T: Complex64[LDV2T, Flat],
    LDV2T: Addr(Int32),
    B11D: Float32[Flat],
    B11E: Float32[Flat],
    B12D: Float32[Flat],
    B12E: Float32[Flat],
    B21D: Float32[Flat],
    B21E: Float32[Flat],
    B22D: Float32[Flat],
    B22E: Float32[Flat],
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CBDSQR")
@external
def cbdsqr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NCVT: Addr(Int32),
    NRU: Addr(Int32),
    NCC: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VT: Complex64[LDVT, Flat],
    LDVT: Addr(Int32),
    U: Complex64[LDU, Flat],
    LDU: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBBRD")
@external
def cgbbrd(
    VECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NCC: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    PT: Complex64[LDPT, Flat],
    LDPT: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBCON")
@external
def cgbcon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBEQU")
@external
def cgbequ(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBEQUB")
@external
def cgbequb(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBRFS")
@external
def cgbrfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBRFSX")
@external
def cgbrfsx(
    TRANS: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBSV")
@external
def cgbsv(
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBSVX")
@external
def cgbsvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBSVXX")
@external
def cgbsvxx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    RPVGRW: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBTF2")
@external
def cgbtf2(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBTRF")
@external
def cgbtrf(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGBTRS")
@external
def cgbtrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEBAK")
@external
def cgebak(
    JOB: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float32[Flat],
    M: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEBAL")
@external
def cgebal(
    JOB: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEBD2")
@external
def cgebd2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Complex64[Flat],
    TAUP: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEBRD")
@external
def cgebrd(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Complex64[Flat],
    TAUP: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGECON")
@external
def cgecon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Addr(Arg(11)), Addr(Arg(12)), Return('K', 0), Arg(13), Arg(14), Addr(Arg(15)), Arg(16), Arg(17), Addr(Arg(18)), Arg(19), Addr(Arg(20)), Arg(21), Addr(Arg(22)), Arg(23), Addr(Arg(24)), Arg(25), Addr(Arg(26)), Arg(27), Addr(Arg(28)), Return('INFO', 10)])
def cgedmd(
    JOBS: Addr(Const(String[1])),
    JOBZ: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBF: Addr(Const(String[1])),
    WHTSVD: Const(Int32),
    M: Const(Int32),
    N: Const(Int32),
    X: Complex64[LDX, Flat],
    LDX: Const(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Const(Int32),
    NRNK: Const(Int32),
    TOL: Const(Float32),
    EIGS: Complex64[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Const(Int32),
    RES: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Const(Int32),
    W: Complex64[LDW, Flat],
    LDW: Const(Int32),
    S: Complex64[LDS, Flat],
    LDS: Const(Int32),
    ZWORK: Complex64[Flat],
    LZWORK: Const(Int32),
    RWORK: Float32[Flat],
    LRWORK: Const(Int32),
    IWORK: Int32[Flat],
    LIWORK: Const(Int32)
) -> tuple[Int32, Returns["EIGS", Complex64[Flat]], Returns["Z", Complex64[LDZ, Flat]], Returns["RES", Float32[Flat]], Returns["B", Complex64[LDB, Flat]], Returns["W", Complex64[LDW, Flat]], Returns["S", Complex64[LDS, Flat]], Returns["ZWORK", Complex64[Flat]], Returns["RWORK", Float32[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("CGEDMDQ")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Arg(11), Addr(Arg(12)), Arg(13), Addr(Arg(14)), Addr(Arg(15)), Addr(Arg(16)), Return('K', 2), Arg(17), Arg(18), Addr(Arg(19)), Arg(20), Arg(21), Addr(Arg(22)), Arg(23), Addr(Arg(24)), Arg(25), Addr(Arg(26)), Arg(27), Addr(Arg(28)), Arg(29), Addr(Arg(30)), Arg(31), Addr(Arg(32)), Return('INFO', 12)])
def cgedmdq(
    JOBS: Addr(Const(String[1])),
    JOBZ: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    JOBT: Addr(Const(String[1])),
    JOBF: Addr(Const(String[1])),
    WHTSVD: Const(Int32),
    M: Const(Int32),
    N: Const(Int32),
    F: Complex64[LDF, Flat],
    LDF: Const(Int32),
    X: Complex64[LDX, Flat],
    LDX: Const(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Const(Int32),
    NRNK: Const(Int32),
    TOL: Const(Float32),
    EIGS: Complex64[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Const(Int32),
    RES: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Const(Int32),
    V: Complex64[LDV, Flat],
    LDV: Const(Int32),
    S: Complex64[LDS, Flat],
    LDS: Const(Int32),
    ZWORK: Complex64[Flat],
    LZWORK: Const(Int32),
    WORK: Float32[Flat],
    LWORK: Const(Int32),
    IWORK: Int32[Flat],
    LIWORK: Const(Int32)
) -> tuple[Returns["X", Complex64[LDX, Flat]], Returns["Y", Complex64[LDY, Flat]], Int32, Returns["EIGS", Complex64[Flat]], Returns["Z", Complex64[LDZ, Flat]], Returns["RES", Float32[Flat]], Returns["B", Complex64[LDB, Flat]], Returns["V", Complex64[LDV, Flat]], Returns["S", Complex64[LDS, Flat]], Returns["ZWORK", Complex64[Flat]], Returns["WORK", Float32[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("CGEEQU")
@external
def cgeequ(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEEQUB")
@external
def cgeequb(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEES")
@external
def cgees(
    JOBVS: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELECT: Addr(Bool),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    SDIM: Addr(Int32),
    W: Complex64[Flat],
    VS: Complex64[LDVS, Flat],
    LDVS: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEESX")
@external
def cgeesx(
    JOBVS: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELECT: Addr(Bool),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    SDIM: Addr(Int32),
    W: Complex64[Flat],
    VS: Complex64[LDVS, Flat],
    LDVS: Addr(Int32),
    RCONDE: Addr(Float32),
    RCONDV: Addr(Float32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEEV")
@external
def cgeev(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    W: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEEVX")
@external
def cgeevx(
    BALANC: Addr(Const(String[1])),
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    W: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float32[Flat],
    ABNRM: Addr(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEHD2")
@external
def cgehd2(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEHRD")
@external
def cgehrd(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEJSV")
@external
def cgejsv(
    JOBA: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBT: Addr(Const(String[1])),
    JOBP: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    SVA: Float32[N],
    U: Complex64[LDU, Flat],
    LDU: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    CWORK: Complex64[LWORK],
    LWORK: Addr(Int32),
    RWORK: Float32[LRWORK],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGELQ")
@external
def cgelq(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[Flat],
    TSIZE: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGELQ2")
@external
def cgelq2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGELQF")
@external
def cgelqf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGELQT")
@external
def cgelqt(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGELQT3")
@external
def cgelqt3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGELS")
@external
def cgels(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGELSD")
@external
def cgelsd(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    S: Float32[Flat],
    RCOND: Addr(Float32),
    RANK: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGELSS")
@external
def cgelss(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    S: Float32[Flat],
    RCOND: Addr(Float32),
    RANK: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGELST")
@external
def cgelst(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGELSY")
@external
def cgelsy(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    JPVT: Int32[Flat],
    RCOND: Addr(Float32),
    RANK: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEMLQ")
@external
def cgemlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[Flat],
    TSIZE: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEMLQT")
@external
def cgemlqt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEMQR")
@external
def cgemqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[Flat],
    TSIZE: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEMQRT")
@external
def cgemqrt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    NB: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQL2")
@external
def cgeql2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQLF")
@external
def cgeqlf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQP3")
@external
def cgeqp3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQP3RK")
@external
def cgeqp3rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    KMAX: Addr(Int32),
    ABSTOL: Addr(Float32),
    RELTOL: Addr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    K: Addr(Int32),
    MAXC2NRMK: Addr(Float32),
    RELMAXC2NRMK: Addr(Float32),
    JPIV: Int32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQR")
@external
def cgeqr(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[Flat],
    TSIZE: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQR2")
@external
def cgeqr2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQR2P")
@external
def cgeqr2p(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQRF")
@external
def cgeqrf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQRFP")
@external
def cgeqrfp(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQRT")
@external
def cgeqrt(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQRT2")
@external
def cgeqrt2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGEQRT3")
@external
def cgeqrt3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGERFS")
@external
def cgerfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGERFSX")
@external
def cgerfsx(
    TRANS: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGERQ2")
@external
def cgerq2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGERQF")
@external
def cgerqf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGESC2")
@external
def cgesc2(
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    RHS: Complex64[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Addr(Float32)
) -> None: ...

@bind("CGESDD")
@external
def cgesdd(
    JOBZ: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Complex64[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGESV")
@external
def cgesv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGESVD")
@external
def cgesvd(
    JOBU: Addr(Const(String[1])),
    JOBVT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Complex64[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGESVDQ")
@external
def cgesvdq(
    JOBA: Addr(Const(String[1])),
    JOBP: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    NUMRANK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    CWORK: Complex64[Flat],
    LCWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGESVDX")
@external
def cgesvdx(
    JOBU: Addr(Const(String[1])),
    JOBVT: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    NS: Addr(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Complex64[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGESVJ")
@external
def cgesvj(
    JOBA: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    SVA: Float32[N],
    MV: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    CWORK: Complex64[LWORK],
    LWORK: Addr(Int32),
    RWORK: Float32[LRWORK],
    LRWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGESVX")
@external
def cgesvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGESVXX")
@external
def cgesvxx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    RPVGRW: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGETC2")
@external
def cgetc2(
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGETF2")
@external
def cgetf2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGETRF")
@external
def cgetrf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGETRF2")
@external
def cgetrf2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGETRI")
@external
def cgetri(
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGETRS")
@external
def cgetrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGETSLS")
@external
def cgetsls(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGETSQRHRT")
@external
def cgetsqrhrt(
    M: Addr(Int32),
    N: Addr(Int32),
    MB1: Addr(Int32),
    NB1: Addr(Int32),
    NB2: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGBAK")
@external
def cggbak(
    JOB: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    M: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGBAL")
@external
def cggbal(
    JOB: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGES")
@external
def cgges(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VSL: Complex64[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Complex64[LDVSR, Flat],
    LDVSR: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGES3")
@external
def cgges3(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VSL: Complex64[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Complex64[LDVSR, Flat],
    LDVSR: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGESX")
@external
def cggesx(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VSL: Complex64[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Complex64[LDVSR, Flat],
    LDVSR: Addr(Int32),
    RCONDE: Float32[2],
    RCONDV: Float32[2],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGEV")
@external
def cggev(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGEV3")
@external
def cggev3(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGEVX")
@external
def cggevx(
    BALANC: Addr(Const(String[1])),
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    ABNRM: Addr(Float32),
    BBNRM: Addr(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGGLM")
@external
def cggglm(
    N: Addr(Int32),
    M: Addr(Int32),
    P: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    D: Complex64[Flat],
    X: Complex64[Flat],
    Y: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGHD3")
@external
def cgghd3(
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGHRD")
@external
def cgghrd(
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGLSE")
@external
def cgglse(
    M: Addr(Int32),
    N: Addr(Int32),
    P: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex64[Flat],
    D: Complex64[Flat],
    X: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGQRF")
@external
def cggqrf(
    N: Addr(Int32),
    M: Addr(Int32),
    P: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAUA: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    TAUB: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGRQF")
@external
def cggrqf(
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAUA: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    TAUB: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGSVD3")
@external
def cggsvd3(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    P: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGGSVP3")
@external
def cggsvp3(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    TOLA: Addr(Float32),
    TOLB: Addr(Float32),
    K: Addr(Int32),
    L: Addr(Int32),
    U: Complex64[LDU, Flat],
    LDU: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    IWORK: Int32[Flat],
    RWORK: Float32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGSVJ0")
@external
def cgsvj0(
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    D: Complex64[N],
    SVA: Float32[N],
    MV: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    EPS: Addr(Float32),
    SFMIN: Addr(Float32),
    TOL: Addr(Float32),
    NSWEEP: Addr(Int32),
    WORK: Complex64[LWORK],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGSVJ1")
@external
def cgsvj1(
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    D: Complex64[N],
    SVA: Float32[N],
    MV: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    EPS: Addr(Float32),
    SFMIN: Addr(Float32),
    TOL: Addr(Float32),
    NSWEEP: Addr(Int32),
    WORK: Complex64[LWORK],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGTCON")
@external
def cgtcon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGTRFS")
@external
def cgtrfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DLF: Complex64[Flat],
    DF: Complex64[Flat],
    DUF: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGTSV")
@external
def cgtsv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGTSVX")
@external
def cgtsvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DLF: Complex64[Flat],
    DF: Complex64[Flat],
    DUF: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGTTRF")
@external
def cgttrf(
    N: Addr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CGTTRS")
@external
def cgttrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CGTTS2")
@external
def cgtts2(
    ITRANS: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("CHB2ST_KERNELS")
@external
def chb2st_kernels(
    UPLO: Addr(Const(String[1])),
    WANTZ: Addr(Bool),
    TTYPE: Addr(Int32),
    ST: Addr(Int32),
    ED: Addr(Int32),
    SWEEP: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    IB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    V: Complex64[Flat],
    TAU: Complex64[Flat],
    LDVT: Addr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CHBEV")
@external
def chbev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHBEV_2STAGE")
@external
def chbev_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHBEVD")
@external
def chbevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHBEVD_2STAGE")
@external
def chbevd_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHBEVX")
@external
def chbevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHBEVX_2STAGE")
@external
def chbevx_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHBGST")
@external
def chbgst(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHBGV")
@external
def chbgv(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHBGVD")
@external
def chbgvd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHBGVX")
@external
def chbgvx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHBTRD")
@external
def chbtrd(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHECON")
@external
def checon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHECON_3")
@external
def checon_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHECON_ROOK")
@external
def checon_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEEQUB")
@external
def cheequb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEEV")
@external
def cheev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEEV_2STAGE")
@external
def cheev_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEEVD")
@external
def cheevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEEVD_2STAGE")
@external
def cheevd_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEEVR")
@external
def cheevr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEEVR_2STAGE")
@external
def cheevr_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEEVX")
@external
def cheevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEEVX_2STAGE")
@external
def cheevx_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEGS2")
@external
def chegs2(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEGST")
@external
def chegst(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEGV")
@external
def chegv(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEGV_2STAGE")
@external
def chegv_2stage(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEGVD")
@external
def chegvd(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHEGVX")
@external
def chegvx(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHERFS")
@external
def cherfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHERFSX")
@external
def cherfsx(
    UPLO: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHESV")
@external
def chesv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHESV_AA")
@external
def chesv_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHESV_AA_2STAGE")
@external
def chesv_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex64[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHESV_RK")
@external
def chesv_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHESV_ROOK")
@external
def chesv_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHESVX")
@external
def chesvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHESVXX")
@external
def chesvxx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    RPVGRW: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHESWAPR")
@external
def cheswapr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex64[LDA, N], ORDER_F],
    LDA: Addr(Int32),
    I1: Addr(Int32),
    I2: Addr(Int32)
) -> None: ...

@bind("CHETD2")
@external
def chetd2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETF2")
@external
def chetf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETF2_RK")
@external
def chetf2_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETF2_ROOK")
@external
def chetf2_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRD")
@external
def chetrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRD_2STAGE")
@external
def chetrd_2stage(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    HOUS2: Complex64[Flat],
    LHOUS2: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRD_HB2ST")
@external
def chetrd_hb2st(
    STAGE1: Addr(Const(String[1])),
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    HOUS: Complex64[Flat],
    LHOUS: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRD_HE2HB")
@external
def chetrd_he2hb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRF")
@external
def chetrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRF_AA")
@external
def chetrf_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRF_AA_2STAGE")
@external
def chetrf_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex64[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRF_RK")
@external
def chetrf_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRF_ROOK")
@external
def chetrf_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRI")
@external
def chetri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRI2")
@external
def chetri2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRI2X")
@external
def chetri2x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRI_3")
@external
def chetri_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRI_3X")
@external
def chetri_3x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRI_ROOK")
@external
def chetri_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRS")
@external
def chetrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRS2")
@external
def chetrs2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRS_3")
@external
def chetrs_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRS_AA")
@external
def chetrs_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRS_AA_2STAGE")
@external
def chetrs_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex64[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHETRS_ROOK")
@external
def chetrs_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHFRK")
@external
def chfrk(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    BETA: Addr(Float32),
    C: Complex64[Flat]
) -> None: ...

@bind("CHGEQZ")
@external
def chgeqz(
    JOB: Addr(Const(String[1])),
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHLA_TRANSTYPE")
@external
def chla_transtype(
    TRANS: Addr(Int32)
) -> String[1]: ...

@bind("CHPCON")
@external
def chpcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPEV")
@external
def chpev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPEVD")
@external
def chpevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPEVX")
@external
def chpevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPGST")
@external
def chpgst(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPGV")
@external
def chpgv(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPGVD")
@external
def chpgvd(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPGVX")
@external
def chpgvx(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPRFS")
@external
def chprfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPSV")
@external
def chpsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPSVX")
@external
def chpsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPTRD")
@external
def chptrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPTRF")
@external
def chptrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPTRI")
@external
def chptri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHPTRS")
@external
def chptrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CHSEIN")
@external
def chsein(
    SIDE: Addr(Const(String[1])),
    EIGSRC: Addr(Const(String[1])),
    INITV: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    W: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CHSEQR")
@external
def chseqr(
    JOB: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    W: Complex64[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLA_GBAMV")
@external
def cla_gbamv(
    TRANS: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    ALPHA: Addr(Float32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float32),
    Y: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CLA_GBRCOND_C")
@external
def cla_gbrcond_c(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Addr(Bool),
    INFO: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GBRCOND_X")
@external
def cla_gbrcond_x(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GBRFSX_EXTENDED")
@external
def cla_gbrfsx_extended(
    PREC_TYPE: Addr(Int32),
    TRANS_TYPE: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Addr(Float32),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float32),
    DZ_UB: Addr(Float32),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLA_GBRPVGRW")
@external
def cla_gbrpvgrw(
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NCOLS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Addr(Int32)
) -> Float32: ...

@bind("CLA_GEAMV")
@external
def cla_geamv(
    TRANS: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float32),
    Y: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CLA_GERCOND_C")
@external
def cla_gercond_c(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Addr(Bool),
    INFO: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GERCOND_X")
@external
def cla_gercond_x(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GERFSX_EXTENDED")
@external
def cla_gerfsx_extended(
    PREC_TYPE: Addr(Int32),
    TRANS_TYPE: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Addr(Int32),
    ERRS_N: Float32[NRHS, Flat],
    ERRS_C: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Addr(Float32),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float32),
    DZ_UB: Addr(Float32),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLA_GERPVGRW")
@external
def cla_gerpvgrw(
    N: Addr(Int32),
    NCOLS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32)
) -> Float32: ...

@bind("CLA_HEAMV")
@external
def cla_heamv(
    UPLO: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float32),
    Y: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CLA_HERCOND_C")
@external
def cla_hercond_c(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Addr(Bool),
    INFO: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_HERCOND_X")
@external
def cla_hercond_x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_HERFSX_EXTENDED")
@external
def cla_herfsx_extended(
    PREC_TYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Addr(Float32),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float32),
    DZ_UB: Addr(Float32),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLA_HERPVGRW")
@external
def cla_herpvgrw(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    INFO: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_LIN_BERR")
@external
def cla_lin_berr(
    N: Addr(Int32),
    NZ: Addr(Int32),
    NRHS: Addr(Int32),
    RES: Annotated[Complex64[N, NRHS], ORDER_F],
    AYB: Annotated[Float32[N, NRHS], ORDER_F],
    BERR: Float32[NRHS]
) -> None: ...

@bind("CLA_PORCOND_C")
@external
def cla_porcond_c(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    C: Float32[Flat],
    CAPPLY: Addr(Bool),
    INFO: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_PORCOND_X")
@external
def cla_porcond_x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    X: Complex64[Flat],
    INFO: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_PORFSX_EXTENDED")
@external
def cla_porfsx_extended(
    PREC_TYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    COLEQU: Addr(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Addr(Float32),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float32),
    DZ_UB: Addr(Float32),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLA_PORPVGRW")
@external
def cla_porpvgrw(
    UPLO: Addr(Const(String[1])),
    NCOLS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_SYAMV")
@external
def cla_syamv(
    UPLO: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float32),
    Y: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CLA_SYRCOND_C")
@external
def cla_syrcond_c(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Addr(Bool),
    INFO: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_SYRCOND_X")
@external
def cla_syrcond_x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_SYRFSX_EXTENDED")
@external
def cla_syrfsx_extended(
    PREC_TYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Addr(Float32),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float32),
    DZ_UB: Addr(Float32),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLA_SYRPVGRW")
@external
def cla_syrpvgrw(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    INFO: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_WWADDW")
@external
def cla_wwaddw(
    N: Addr(Int32),
    X: Complex64[Flat],
    Y: Complex64[Flat],
    W: Complex64[Flat]
) -> None: ...

@bind("CLABRD")
@external
def clabrd(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Complex64[Flat],
    TAUP: Complex64[Flat],
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Addr(Int32)
) -> None: ...

@bind("CLACGV")
@external
def clacgv(
    N: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CLACN2")
@external
def clacn2(
    N: Addr(Int32),
    V: Complex64[Flat],
    X: Complex64[Flat],
    EST: Addr(Float32),
    KASE: Addr(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("CLACON")
@external
def clacon(
    N: Addr(Int32),
    V: Complex64[N],
    X: Complex64[N],
    EST: Addr(Float32),
    KASE: Addr(Int32)
) -> None: ...

@bind("CLACP2")
@external
def clacp2(
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("CLACPY")
@external
def clacpy(
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("CLACRM")
@external
def clacrm(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    RWORK: Float32[Flat]
) -> None: ...

@bind("CLACRT")
@external
def clacrt(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32),
    CY: Complex64[Flat],
    INCY: Addr(Int32),
    C: Addr(Complex64),
    S: Addr(Complex64)
) -> None: ...

@bind("CLADIV")
@external
def cladiv(
    X: Addr(Complex64),
    Y: Addr(Complex64)
) -> Complex64: ...

@bind("CLAED0")
@external
def claed0(
    QSIZ: Addr(Int32),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    QSTORE: Complex64[LDQS, Flat],
    LDQS: Addr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAED7")
@external
def claed7(
    N: Addr(Int32),
    CUTPNT: Addr(Int32),
    QSIZ: Addr(Int32),
    TLVLS: Addr(Int32),
    CURLVL: Addr(Int32),
    CURPBM: Addr(Int32),
    D: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    RHO: Addr(Float32),
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
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAED8")
@external
def claed8(
    K: Addr(Int32),
    N: Addr(Int32),
    QSIZ: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    D: Float32[Flat],
    RHO: Addr(Float32),
    CUTPNT: Addr(Int32),
    Z: Float32[Flat],
    DLAMBDA: Float32[Flat],
    Q2: Complex64[LDQ2, Flat],
    LDQ2: Addr(Int32),
    W: Float32[Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAEIN")
@external
def claein(
    RIGHTV: Addr(Bool),
    NOINIT: Addr(Bool),
    N: Addr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    W: Addr(Complex64),
    V: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    RWORK: Float32[Flat],
    EPS3: Addr(Float32),
    SMLNUM: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAESY")
@external
def claesy(
    A: Addr(Complex64),
    B: Addr(Complex64),
    C: Addr(Complex64),
    RT1: Addr(Complex64),
    RT2: Addr(Complex64),
    EVSCAL: Addr(Complex64),
    CS1: Addr(Complex64),
    SN1: Addr(Complex64)
) -> None: ...

@bind("CLAEV2")
@external
def claev2(
    A: Addr(Complex64),
    B: Addr(Complex64),
    C: Addr(Complex64),
    RT1: Addr(Float32),
    RT2: Addr(Float32),
    CS1: Addr(Float32),
    SN1: Addr(Complex64)
) -> None: ...

@bind("CLAG2Z")
@external
def clag2z(
    M: Addr(Int32),
    N: Addr(Int32),
    SA: Complex64[LDSA, Flat],
    LDSA: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAGS2")
@external
def clags2(
    UPPER: Addr(Bool),
    A1: Addr(Float32),
    A2: Addr(Complex64),
    A3: Addr(Float32),
    B1: Addr(Float32),
    B2: Addr(Complex64),
    B3: Addr(Float32),
    CSU: Addr(Float32),
    SNU: Addr(Complex64),
    CSV: Addr(Float32),
    SNV: Addr(Complex64),
    CSQ: Addr(Float32),
    SNQ: Addr(Complex64)
) -> None: ...

@bind("CLAGTM")
@external
def clagtm(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    ALPHA: Addr(Float32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    BETA: Addr(Float32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("CLAHEF")
@external
def clahef(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAHEF_AA")
@external
def clahef_aa(
    UPLO: Addr(Const(String[1])),
    J1: Addr(Int32),
    M: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLAHEF_RK")
@external
def clahef_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAHEF_ROOK")
@external
def clahef_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAHQR")
@external
def clahqr(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    W: Complex64[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAHR2")
@external
def clahr2(
    N: Addr(Int32),
    K: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[NB],
    T: Annotated[Complex64[LDT, NB], ORDER_F],
    LDT: Addr(Int32),
    Y: Annotated[Complex64[LDY, NB], ORDER_F],
    LDY: Addr(Int32)
) -> None: ...

@bind("CLAIC1")
@external
def claic1(
    JOB: Addr(Int32),
    J: Addr(Int32),
    X: Complex64[J],
    SEST: Addr(Float32),
    W: Complex64[J],
    GAMMA: Addr(Complex64),
    SESTPR: Addr(Float32),
    S: Addr(Complex64),
    C: Addr(Complex64)
) -> None: ...

@bind("CLALS0")
@external
def clals0(
    ICOMPQ: Addr(Int32),
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    NRHS: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    BX: Complex64[LDBX, Flat],
    LDBX: Addr(Int32),
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Addr(Int32),
    POLES: Float32[LDGNUM, Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[LDGNUM, Flat],
    Z: Float32[Flat],
    K: Addr(Int32),
    C: Addr(Float32),
    S: Addr(Float32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLALSA")
@external
def clalsa(
    ICOMPQ: Addr(Int32),
    SMLSIZ: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    BX: Complex64[LDBX, Flat],
    LDBX: Addr(Int32),
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float32[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float32[LDU, Flat],
    DIFR: Float32[LDU, Flat],
    Z: Float32[LDU, Flat],
    POLES: Float32[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float32[LDU, Flat],
    C: Float32[Flat],
    S: Float32[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLALSD")
@external
def clalsd(
    UPLO: Addr(Const(String[1])),
    SMLSIZ: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    RCOND: Addr(Float32),
    RANK: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAMSWLQ")
@external
def clamswlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAMTSQR")
@external
def clamtsqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLANGB")
@external
def clangb(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANGE")
@external
def clange(
    NORM: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANGT")
@external
def clangt(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat]
) -> Float32: ...

@bind("CLANHB")
@external
def clanhb(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHE")
@external
def clanhe(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHF")
@external
def clanhf(
    NORM: Addr(Const(String[1])),
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    WORK: Annotated[Float32[Flat], SourceDims("0:*")]
) -> Float32: ...

@bind("CLANHP")
@external
def clanhp(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHS")
@external
def clanhs(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHT")
@external
def clanht(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat]
) -> Float32: ...

@bind("CLANSB")
@external
def clansb(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANSP")
@external
def clansp(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANSY")
@external
def clansy(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANTB")
@external
def clantb(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANTP")
@external
def clantp(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANTR")
@external
def clantr(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLAPLL")
@external
def clapll(
    N: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    Y: Complex64[Flat],
    INCY: Addr(Int32),
    SSMIN: Addr(Float32)
) -> None: ...

@bind("CLAPMR")
@external
def clapmr(
    FORWRD: Addr(Bool),
    M: Addr(Int32),
    N: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("CLAPMT")
@external
def clapmt(
    FORWRD: Addr(Bool),
    M: Addr(Int32),
    N: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("CLAQGB")
@external
def claqgb(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("CLAQGE")
@external
def claqge(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("CLAQHB")
@external
def claqhb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("CLAQHE")
@external
def claqhe(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("CLAQHP")
@external
def claqhp(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("CLAQP2")
@external
def claqp2(
    M: Addr(Int32),
    N: Addr(Int32),
    OFFSET: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLAQP2RK")
@external
def claqp2rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    IOFFSET: Addr(Int32),
    KMAX: Addr(Int32),
    ABSTOL: Addr(Float32),
    RELTOL: Addr(Float32),
    KP1: Addr(Int32),
    MAXC2NRM: Addr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    K: Addr(Int32),
    MAXC2NRMK: Addr(Float32),
    RELMAXC2NRMK: Addr(Float32),
    JPIV: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAQP3RK")
@external
def claqp3rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    IOFFSET: Addr(Int32),
    NB: Addr(Int32),
    ABSTOL: Addr(Float32),
    RELTOL: Addr(Float32),
    KP1: Addr(Int32),
    MAXC2NRM: Addr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    DONE: Addr(Bool),
    KB: Addr(Int32),
    MAXC2NRMK: Addr(Float32),
    RELMAXC2NRMK: Addr(Float32),
    JPIV: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Complex64[Flat],
    F: Complex64[LDF, Flat],
    LDF: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAQPS")
@external
def claqps(
    M: Addr(Int32),
    N: Addr(Int32),
    OFFSET: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Complex64[Flat],
    F: Complex64[LDF, Flat],
    LDF: Addr(Int32)
) -> None: ...

@bind("CLAQR0")
@external
def claqr0(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    W: Complex64[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAQR1")
@external
def claqr1(
    N: Addr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    S1: Addr(Complex64),
    S2: Addr(Complex64),
    V: Complex64[Flat]
) -> None: ...

@bind("CLAQR2")
@external
def claqr2(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NW: Addr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    NS: Addr(Int32),
    ND: Addr(Int32),
    SH: Complex64[Flat],
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    NH: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    NV: Addr(Int32),
    WV: Complex64[LDWV, Flat],
    LDWV: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32)
) -> None: ...

@bind("CLAQR3")
@external
def claqr3(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NW: Addr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    NS: Addr(Int32),
    ND: Addr(Int32),
    SH: Complex64[Flat],
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    NH: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    NV: Addr(Int32),
    WV: Complex64[LDWV, Flat],
    LDWV: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32)
) -> None: ...

@bind("CLAQR4")
@external
def claqr4(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    W: Complex64[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAQR5")
@external
def claqr5(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    KACC22: Addr(Int32),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NSHFTS: Addr(Int32),
    S: Complex64[Flat],
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    U: Complex64[LDU, Flat],
    LDU: Addr(Int32),
    NV: Addr(Int32),
    WV: Complex64[LDWV, Flat],
    LDWV: Addr(Int32),
    NH: Addr(Int32),
    WH: Complex64[LDWH, Flat],
    LDWH: Addr(Int32)
) -> None: ...

@bind("CLAQSB")
@external
def claqsb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("CLAQSP")
@external
def claqsp(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("CLAQSY")
@external
def claqsy(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("CLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Arg(10), Arg(11), Arg(12), Addr(Arg(13)), Arg(14), Addr(Arg(15)), Arg(16), Addr(Arg(17)), Arg(18), Addr(Arg(19)), Return('INFO', 1)])
def claqz0(
    WANTS: Addr(Const(String[1])),
    WANTQ: Addr(Const(String[1])),
    WANTZ: Addr(Const(String[1])),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    A: Complex64[LDA, Flat],
    LDA: Const(Int32),
    B: Complex64[LDB, Flat],
    LDB: Const(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Const(Int32),
    WORK: Complex64[Flat],
    LWORK: Const(Int32),
    RWORK: Float32[Flat],
    REC: Const(Int32)
) -> tuple[Returns["RWORK", Float32[Flat]], Int32]: ...

@bind("CLAQZ1")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Addr(Arg(11)), Arg(12), Addr(Arg(13)), Addr(Arg(14)), Addr(Arg(15)), Arg(16), Addr(Arg(17))])
def claqz1(
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    K: Const(Int32),
    ISTARTM: Const(Int32),
    ISTOPM: Const(Int32),
    IHI: Const(Int32),
    A: Complex64[LDA, Flat],
    LDA: Const(Int32),
    B: Complex64[LDB, Flat],
    LDB: Const(Int32),
    NQ: Const(Int32),
    QSTART: Const(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Const(Int32),
    NZ: Const(Int32),
    ZSTART: Const(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Const(Int32)
) -> None: ...

@bind("CLAQZ2")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Arg(11), Addr(Arg(12)), Arg(13), Addr(Arg(14)), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Addr(Arg(18)), Arg(19), Addr(Arg(20)), Arg(21), Addr(Arg(22)), Arg(23), Addr(Arg(24)), Return('INFO', 2)])
def claqz2(
    ILSCHUR: Const(Bool),
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    NW: Const(Int32),
    A: Complex64[LDA, Flat],
    LDA: Const(Int32),
    B: Complex64[LDB, Flat],
    LDB: Const(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Const(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    QC: Complex64[LDQC, Flat],
    LDQC: Const(Int32),
    ZC: Complex64[LDZC, Flat],
    LDZC: Const(Int32),
    WORK: Complex64[Flat],
    LWORK: Const(Int32),
    RWORK: Float32[Flat],
    REC: Const(Int32)
) -> tuple[Int32, Int32, Int32]: ...

@bind("CLAQZ3")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Arg(9), Arg(10), Addr(Arg(11)), Arg(12), Addr(Arg(13)), Arg(14), Addr(Arg(15)), Arg(16), Addr(Arg(17)), Arg(18), Addr(Arg(19)), Arg(20), Addr(Arg(21)), Arg(22), Addr(Arg(23)), Return('INFO', 0)])
def claqz3(
    ILSCHUR: Const(Bool),
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    NSHIFTS: Const(Int32),
    NBLOCK_DESIRED: Const(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    A: Complex64[LDA, Flat],
    LDA: Const(Int32),
    B: Complex64[LDB, Flat],
    LDB: Const(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Const(Int32),
    QC: Complex64[LDQC, Flat],
    LDQC: Const(Int32),
    ZC: Complex64[LDZC, Flat],
    LDZC: Const(Int32),
    WORK: Complex64[Flat],
    LWORK: Const(Int32)
) -> Int32: ...

@bind("CLAR1V")
@external
def clar1v(
    N: Addr(Int32),
    B1: Addr(Int32),
    BN: Addr(Int32),
    LAMBDA: Addr(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    LD: Float32[Flat],
    LLD: Float32[Flat],
    PIVMIN: Addr(Float32),
    GAPTOL: Addr(Float32),
    Z: Complex64[Flat],
    WANTNC: Addr(Bool),
    NEGCNT: Addr(Int32),
    ZTZ: Addr(Float32),
    MINGMA: Addr(Float32),
    R: Addr(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Addr(Float32),
    RESID: Addr(Float32),
    RQCORR: Addr(Float32),
    WORK: Float32[Flat]
) -> None: ...

@bind("CLAR2V")
@external
def clar2v(
    N: Addr(Int32),
    X: Complex64[Flat],
    Y: Complex64[Flat],
    Z: Complex64[Flat],
    INCX: Addr(Int32),
    C: Float32[Flat],
    S: Complex64[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("CLARCM")
@external
def clarcm(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    RWORK: Float32[Flat]
) -> None: ...

@bind("CLARF")
@external
def clarf(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Complex64[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARF1F")
@external
def clarf1f(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Complex64[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARF1L")
@external
def clarf1l(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Complex64[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARFB")
@external
def clarfb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("CLARFB_GETT")
@external
def clarfb_gett(
    IDENT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("CLARFG")
@external
def clarfg(
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    TAU: Addr(Complex64)
) -> None: ...

@bind("CLARFGP")
@external
def clarfgp(
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    TAU: Addr(Complex64)
) -> None: ...

@bind("CLARFT")
@external
def clarft(
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    TAU: Complex64[Flat],
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32)
) -> None: ...

@bind("CLARFX")
@external
def clarfx(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Complex64[Flat],
    TAU: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARFY")
@external
def clarfy(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    V: Complex64[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARGV")
@external
def clargv(
    N: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    Y: Complex64[Flat],
    INCY: Addr(Int32),
    C: Float32[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("CLARNV")
@external
def clarnv(
    IDIST: Addr(Int32),
    ISEED: Int32[4],
    N: Addr(Int32),
    X: Complex64[Flat]
) -> None: ...

@bind("CLARRV")
@external
def clarrv(
    N: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    PIVMIN: Addr(Float32),
    ISPLIT: Int32[Flat],
    M: Addr(Int32),
    DOL: Addr(Int32),
    DOU: Addr(Int32),
    MINRGP: Addr(Float32),
    RTOL1: Addr(Float32),
    RTOL2: Addr(Float32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WGAP: Float32[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLARSCL2")
@external
def clarscl2(
    M: Addr(Int32),
    N: Addr(Int32),
    D: Float32[Flat],
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32)
) -> None: ...

@bind("CLARTG")
@external
def clartg(
    f: Addr(Complex64),
    g: Addr(Complex64),
    c: Addr(Float32),
    s: Addr(Complex64),
    r: Addr(Complex64)
) -> None: ...

@bind("CLARTV")
@external
def clartv(
    N: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    Y: Complex64[Flat],
    INCY: Addr(Int32),
    C: Float32[Flat],
    S: Complex64[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("CLARZ")
@external
def clarz(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    V: Complex64[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARZB")
@external
def clarzb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("CLARZT")
@external
def clarzt(
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    TAU: Complex64[Flat],
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32)
) -> None: ...

@bind("CLASCL")
@external
def clascl(
    TYPE: Addr(Const(String[1])),
    KL: Addr(Int32),
    KU: Addr(Int32),
    CFROM: Addr(Float32),
    CTO: Addr(Float32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLASCL2")
@external
def clascl2(
    M: Addr(Int32),
    N: Addr(Int32),
    D: Float32[Flat],
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32)
) -> None: ...

@bind("CLASET")
@external
def claset(
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    BETA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("CLASR")
@external
def clasr(
    SIDE: Addr(Const(String[1])),
    PIVOT: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("CLASSQ")
@external
def classq(
    n: Addr(Int32),
    x: Complex64[Flat],
    incx: Addr(Int32),
    scale: Addr(Float32),
    sumsq: Addr(Float32)
) -> None: ...

@bind("CLASWLQ")
@external
def claswlq(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLASWP")
@external
def claswp(
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    K1: Addr(Int32),
    K2: Addr(Int32),
    IPIV: Int32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CLASYF")
@external
def clasyf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLASYF_AA")
@external
def clasyf_aa(
    UPLO: Addr(Const(String[1])),
    J1: Addr(Int32),
    M: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    H: Complex64[LDH, Flat],
    LDH: Addr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLASYF_RK")
@external
def clasyf_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLASYF_ROOK")
@external
def clasyf_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLATBS")
@external
def clatbs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    X: Complex64[Flat],
    SCALE: Addr(Float32),
    CNORM: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLATDF")
@external
def clatdf(
    IJOB: Addr(Int32),
    N: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    RHS: Complex64[Flat],
    RDSUM: Addr(Float32),
    RDSCAL: Addr(Float32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("CLATPS")
@external
def clatps(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    SCALE: Addr(Float32),
    CNORM: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLATRD")
@external
def clatrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    TAU: Complex64[Flat],
    W: Complex64[LDW, Flat],
    LDW: Addr(Int32)
) -> None: ...

@bind("CLATRS")
@external
def clatrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    SCALE: Addr(Float32),
    CNORM: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLATRS3")
@external
def clatrs3(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    SCALE: Float32[Flat],
    CNORM: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLATRZ")
@external
def clatrz(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLATSQR")
@external
def clatsqr(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAUNHR_COL_GETRFNP")
@external
def claunhr_col_getrfnp(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    D: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAUNHR_COL_GETRFNP2")
@external
def claunhr_col_getrfnp2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    D: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAUU2")
@external
def clauu2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CLAUUM")
@external
def clauum(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPBCON")
@external
def cpbcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPBEQU")
@external
def cpbequ(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPBRFS")
@external
def cpbrfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPBSTF")
@external
def cpbstf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPBSV")
@external
def cpbsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPBSVX")
@external
def cpbsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPBTF2")
@external
def cpbtf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPBTRF")
@external
def cpbtrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPBTRS")
@external
def cpbtrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPFTRF")
@external
def cpftrf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPFTRI")
@external
def cpftri(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPFTRS")
@external
def cpftrs(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOCON")
@external
def cpocon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOEQU")
@external
def cpoequ(
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOEQUB")
@external
def cpoequb(
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPORFS")
@external
def cporfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPORFSX")
@external
def cporfsx(
    UPLO: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOSV")
@external
def cposv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOSVX")
@external
def cposvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOSVXX")
@external
def cposvxx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    RPVGRW: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOTF2")
@external
def cpotf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOTRF")
@external
def cpotrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOTRF2")
@external
def cpotrf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOTRI")
@external
def cpotri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPOTRS")
@external
def cpotrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPPCON")
@external
def cppcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPPEQU")
@external
def cppequ(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPPRFS")
@external
def cpprfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPPSV")
@external
def cppsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPPSVX")
@external
def cppsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPPTRF")
@external
def cpptrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPPTRI")
@external
def cpptri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPPTRS")
@external
def cpptrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPSTF2")
@external
def cpstf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    PIV: Int32[N],
    RANK: Addr(Int32),
    TOL: Addr(Float32),
    WORK: Float32[2 * N],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPSTRF")
@external
def cpstrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    PIV: Int32[N],
    RANK: Addr(Int32),
    TOL: Addr(Float32),
    WORK: Float32[2 * N],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPTCON")
@external
def cptcon(
    N: Addr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPTEQR")
@external
def cpteqr(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPTRFS")
@external
def cptrfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    DF: Float32[Flat],
    EF: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPTSV")
@external
def cptsv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPTSVX")
@external
def cptsvx(
    FACT: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    DF: Float32[Flat],
    EF: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPTTRF")
@external
def cpttrf(
    N: Addr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CPTTRS")
@external
def cpttrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CPTTS2")
@external
def cptts2(
    IUPLO: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("CROT")
@external
def crot(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32),
    CY: Complex64[Flat],
    INCY: Addr(Int32),
    C: Addr(Float32),
    S: Addr(Complex64)
) -> None: ...

@bind("CRSCL")
@external
def crscl(
    N: Addr(Int32),
    A: Addr(Complex64),
    X: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CSPCON")
@external
def cspcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSPMV")
@external
def cspmv(
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

@bind("CSPR")
@external
def cspr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    AP: Complex64[Flat]
) -> None: ...

@bind("CSPRFS")
@external
def csprfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSPSV")
@external
def cspsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSPSVX")
@external
def cspsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSPTRF")
@external
def csptrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSPTRI")
@external
def csptri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSPTRS")
@external
def csptrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSRSCL")
@external
def csrscl(
    N: Addr(Int32),
    SA: Addr(Float32),
    SX: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CSTEDC")
@external
def cstedc(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSTEGR")
@external
def cstegr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSTEIN")
@external
def cstein(
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    M: Addr(Int32),
    W: Float32[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSTEMR")
@external
def cstemr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    NZC: Addr(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Addr(Bool),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSTEQR")
@external
def csteqr(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYCON")
@external
def csycon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYCON_3")
@external
def csycon_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYCON_ROOK")
@external
def csycon_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYCONV")
@external
def csyconv(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    E: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYCONVF")
@external
def csyconvf(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYCONVF_ROOK")
@external
def csyconvf_rook(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYEQUB")
@external
def csyequb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYMV")
@external
def csymv(
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

@bind("CSYR")
@external
def csyr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("CSYRFS")
@external
def csyrfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYRFSX")
@external
def csyrfsx(
    UPLO: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYSV")
@external
def csysv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYSV_AA")
@external
def csysv_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYSV_AA_2STAGE")
@external
def csysv_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex64[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYSV_RK")
@external
def csysv_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYSV_ROOK")
@external
def csysv_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYSVX")
@external
def csysvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYSVXX")
@external
def csysvxx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    RPVGRW: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYSWAPR")
@external
def csyswapr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex64[LDA, N], ORDER_F],
    LDA: Addr(Int32),
    I1: Addr(Int32),
    I2: Addr(Int32)
) -> None: ...

@bind("CSYTF2")
@external
def csytf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTF2_RK")
@external
def csytf2_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTF2_ROOK")
@external
def csytf2_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRF")
@external
def csytrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRF_AA")
@external
def csytrf_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRF_AA_2STAGE")
@external
def csytrf_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex64[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRF_RK")
@external
def csytrf_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRF_ROOK")
@external
def csytrf_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRI")
@external
def csytri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRI2")
@external
def csytri2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRI2X")
@external
def csytri2x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRI_3")
@external
def csytri_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRI_3X")
@external
def csytri_3x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRI_ROOK")
@external
def csytri_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRS")
@external
def csytrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRS2")
@external
def csytrs2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRS_3")
@external
def csytrs_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRS_AA")
@external
def csytrs_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRS_AA_2STAGE")
@external
def csytrs_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex64[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CSYTRS_ROOK")
@external
def csytrs_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTBCON")
@external
def ctbcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTBRFS")
@external
def ctbrfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTBTRS")
@external
def ctbtrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTFSM")
@external
def ctfsm(
    TRANSR: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    B: Annotated[Complex64[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Addr(Int32)
) -> None: ...

@bind("CTFTRI")
@external
def ctftri(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTFTTP")
@external
def ctfttp(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    AP: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTFTTR")
@external
def ctfttr(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    A: Annotated[Complex64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTGEVC")
@external
def ctgevc(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    S: Complex64[LDS, Flat],
    LDS: Addr(Int32),
    P: Complex64[LDP, Flat],
    LDP: Addr(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTGEX2")
@external
def ctgex2(
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    J1: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTGEXC")
@external
def ctgexc(
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    IFST: Addr(Int32),
    ILST: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTGSEN")
@external
def ctgsen(
    IJOB: Addr(Int32),
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Addr(Int32),
    M: Addr(Int32),
    PL: Addr(Float32),
    PR: Addr(Float32),
    DIF: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTGSJA")
@external
def ctgsja(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    TOLA: Addr(Float32),
    TOLB: Addr(Float32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Complex64[Flat],
    NCYCLE: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTGSNA")
@external
def ctgsna(
    JOB: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    S: Float32[Flat],
    DIF: Float32[Flat],
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTGSY2")
@external
def ctgsy2(
    TRANS: Addr(Const(String[1])),
    IJOB: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    D: Complex64[LDD, Flat],
    LDD: Addr(Int32),
    E: Complex64[LDE, Flat],
    LDE: Addr(Int32),
    F: Complex64[LDF, Flat],
    LDF: Addr(Int32),
    SCALE: Addr(Float32),
    RDSUM: Addr(Float32),
    RDSCAL: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTGSYL")
@external
def ctgsyl(
    TRANS: Addr(Const(String[1])),
    IJOB: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    D: Complex64[LDD, Flat],
    LDD: Addr(Int32),
    E: Complex64[LDE, Flat],
    LDE: Addr(Int32),
    F: Complex64[LDF, Flat],
    LDF: Addr(Int32),
    SCALE: Addr(Float32),
    DIF: Addr(Float32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPCON")
@external
def ctpcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPLQT")
@external
def ctplqt(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    MB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPLQT2")
@external
def ctplqt2(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPMLQT")
@external
def ctpmlqt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    MB: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPMQRT")
@external
def ctpmqrt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    NB: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPQRT")
@external
def ctpqrt(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPQRT2")
@external
def ctpqrt2(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPRFB")
@external
def ctprfb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("CTPRFS")
@external
def ctprfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPTRI")
@external
def ctptri(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPTRS")
@external
def ctptrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPTTF")
@external
def ctpttf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Annotated[Complex64[Flat], SourceDims("0:*")],
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTPTTR")
@external
def ctpttr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRCON")
@external
def ctrcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    RCOND: Addr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTREVC")
@external
def ctrevc(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTREVC3")
@external
def ctrevc3(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTREXC")
@external
def ctrexc(
    COMPQ: Addr(Const(String[1])),
    N: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    IFST: Addr(Int32),
    ILST: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRRFS")
@external
def ctrrfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRSEN")
@external
def ctrsen(
    JOB: Addr(Const(String[1])),
    COMPQ: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    W: Complex64[Flat],
    M: Addr(Int32),
    S: Addr(Float32),
    SEP: Addr(Float32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRSNA")
@external
def ctrsna(
    JOB: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Addr(Int32),
    S: Float32[Flat],
    SEP: Float32[Flat],
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Addr(Int32),
    RWORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRSYL")
@external
def ctrsyl(
    TRANA: Addr(Const(String[1])),
    TRANB: Addr(Const(String[1])),
    ISGN: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    SCALE: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRSYL3")
@external
def ctrsyl3(
    TRANA: Addr(Const(String[1])),
    TRANB: Addr(Const(String[1])),
    ISGN: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    SCALE: Addr(Float32),
    SWORK: Float32[LDSWORK, Flat],
    LDSWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRTI2")
@external
def ctrti2(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRTRI")
@external
def ctrtri(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRTRS")
@external
def ctrtrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRTTF")
@external
def ctrttf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Addr(Int32),
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTRTTP")
@external
def ctrttp(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    AP: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CTZRZF")
@external
def ctzrzf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNBDB")
@external
def cunbdb(
    TRANS: Addr(Const(String[1])),
    SIGNS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Addr(Int32),
    X12: Complex64[LDX12, Flat],
    LDX12: Addr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Addr(Int32),
    X22: Complex64[LDX22, Flat],
    LDX22: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    TAUQ2: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNBDB1")
@external
def cunbdb1(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNBDB2")
@external
def cunbdb2(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNBDB3")
@external
def cunbdb3(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNBDB4")
@external
def cunbdb4(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    PHANTOM: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNBDB5")
@external
def cunbdb5(
    M1: Addr(Int32),
    M2: Addr(Int32),
    N: Addr(Int32),
    X1: Complex64[Flat],
    INCX1: Addr(Int32),
    X2: Complex64[Flat],
    INCX2: Addr(Int32),
    Q1: Complex64[LDQ1, Flat],
    LDQ1: Addr(Int32),
    Q2: Complex64[LDQ2, Flat],
    LDQ2: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNBDB6")
@external
def cunbdb6(
    M1: Addr(Int32),
    M2: Addr(Int32),
    N: Addr(Int32),
    X1: Complex64[Flat],
    INCX1: Addr(Int32),
    X2: Complex64[Flat],
    INCX2: Addr(Int32),
    Q1: Complex64[LDQ1, Flat],
    LDQ1: Addr(Int32),
    Q2: Complex64[LDQ2, Flat],
    LDQ2: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNCSD")
@external
def cuncsd(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    JOBV2T: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    SIGNS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Addr(Int32),
    X12: Complex64[LDX12, Flat],
    LDX12: Addr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Addr(Int32),
    X22: Complex64[LDX22, Flat],
    LDX22: Addr(Int32),
    THETA: Float32[Flat],
    U1: Complex64[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Complex64[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Complex64[LDV1T, Flat],
    LDV1T: Addr(Int32),
    V2T: Complex64[LDV2T, Flat],
    LDV2T: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNCSD2BY1")
@external
def cuncsd2by1(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float32[Flat],
    U1: Complex64[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Complex64[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Complex64[LDV1T, Flat],
    LDV1T: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNG2L")
@external
def cung2l(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNG2R")
@external
def cung2r(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGBR")
@external
def cungbr(
    VECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGHR")
@external
def cunghr(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGL2")
@external
def cungl2(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGLQ")
@external
def cunglq(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGQL")
@external
def cungql(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGQR")
@external
def cungqr(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGR2")
@external
def cungr2(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGRQ")
@external
def cungrq(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGTR")
@external
def cungtr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGTSQR")
@external
def cungtsqr(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNGTSQR_ROW")
@external
def cungtsqr_row(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNHR_COL")
@external
def cunhr_col(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Addr(Int32),
    D: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNM22")
@external
def cunm22(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    N2: Addr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNM2L")
@external
def cunm2l(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNM2R")
@external
def cunm2r(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNMBR")
@external
def cunmbr(
    VECT: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNMHR")
@external
def cunmhr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNML2")
@external
def cunml2(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNMLQ")
@external
def cunmlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNMQL")
@external
def cunmql(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNMQR")
@external
def cunmqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNMR2")
@external
def cunmr2(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNMR3")
@external
def cunmr3(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNMRQ")
@external
def cunmrq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNMRZ")
@external
def cunmrz(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUNMTR")
@external
def cunmtr(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("CUPGTR")
@external
def cupgtr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    TAU: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("CUPMTR")
@external
def cupmtr(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    AP: Complex64[Flat],
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DBBCSD")
@external
def dbbcsd(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    JOBV2T: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    U1: Float64[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Float64[LDV1T, Flat],
    LDV1T: Addr(Int32),
    V2T: Float64[LDV2T, Flat],
    LDV2T: Addr(Int32),
    B11D: Float64[Flat],
    B11E: Float64[Flat],
    B12D: Float64[Flat],
    B12E: Float64[Flat],
    B21D: Float64[Flat],
    B21E: Float64[Flat],
    B22D: Float64[Flat],
    B22E: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DBDSDC")
@external
def dbdsdc(
    UPLO: Addr(Const(String[1])),
    COMPQ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Addr(Int32),
    Q: Float64[Flat],
    IQ: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DBDSQR")
@external
def dbdsqr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NCVT: Addr(Int32),
    NRU: Addr(Int32),
    NCC: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VT: Float64[LDVT, Flat],
    LDVT: Addr(Int32),
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DBDSVDX")
@external
def dbdsvdx(
    UPLO: Addr(Const(String[1])),
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    NS: Addr(Int32),
    S: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DDISNA")
@external
def ddisna(
    JOB: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    D: Float64[Flat],
    SEP: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBBRD")
@external
def dgbbrd(
    VECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NCC: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    PT: Float64[LDPT, Flat],
    LDPT: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBCON")
@external
def dgbcon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBEQU")
@external
def dgbequ(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBEQUB")
@external
def dgbequb(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBRFS")
@external
def dgbrfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBRFSX")
@external
def dgbrfsx(
    TRANS: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBSV")
@external
def dgbsv(
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBSVX")
@external
def dgbsvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBSVXX")
@external
def dgbsvxx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    RPVGRW: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBTF2")
@external
def dgbtf2(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBTRF")
@external
def dgbtrf(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGBTRS")
@external
def dgbtrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEBAK")
@external
def dgebak(
    JOB: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float64[Flat],
    M: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEBAL")
@external
def dgebal(
    JOB: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEBD2")
@external
def dgebd2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Float64[Flat],
    TAUP: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEBRD")
@external
def dgebrd(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Float64[Flat],
    TAUP: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGECON")
@external
def dgecon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Addr(Arg(11)), Addr(Arg(12)), Return('K', 0), Arg(13), Arg(14), Arg(15), Addr(Arg(16)), Arg(17), Arg(18), Addr(Arg(19)), Arg(20), Addr(Arg(21)), Arg(22), Addr(Arg(23)), Arg(24), Addr(Arg(25)), Arg(26), Addr(Arg(27)), Return('INFO', 10)])
def dgedmd(
    JOBS: Addr(Const(String[1])),
    JOBZ: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBF: Addr(Const(String[1])),
    WHTSVD: Const(Int32),
    M: Const(Int32),
    N: Const(Int32),
    X: Float64[LDX, Flat],
    LDX: Const(Int32),
    Y: Float64[LDY, Flat],
    LDY: Const(Int32),
    NRNK: Const(Int32),
    TOL: Const(Float64),
    REIG: Float64[Flat],
    IMEIG: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Const(Int32),
    RES: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Const(Int32),
    W: Float64[LDW, Flat],
    LDW: Const(Int32),
    S: Float64[LDS, Flat],
    LDS: Const(Int32),
    WORK: Float64[Flat],
    LWORK: Const(Int32),
    IWORK: Int32[Flat],
    LIWORK: Const(Int32)
) -> tuple[Int32, Returns["REIG", Float64[Flat]], Returns["IMEIG", Float64[Flat]], Returns["Z", Float64[LDZ, Flat]], Returns["RES", Float64[Flat]], Returns["B", Float64[LDB, Flat]], Returns["W", Float64[LDW, Flat]], Returns["S", Float64[LDS, Flat]], Returns["WORK", Float64[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("DGEDMDQ")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Arg(11), Addr(Arg(12)), Arg(13), Addr(Arg(14)), Addr(Arg(15)), Addr(Arg(16)), Return('K', 2), Arg(17), Arg(18), Arg(19), Addr(Arg(20)), Arg(21), Arg(22), Addr(Arg(23)), Arg(24), Addr(Arg(25)), Arg(26), Addr(Arg(27)), Arg(28), Addr(Arg(29)), Arg(30), Addr(Arg(31)), Return('INFO', 12)])
def dgedmdq(
    JOBS: Addr(Const(String[1])),
    JOBZ: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    JOBT: Addr(Const(String[1])),
    JOBF: Addr(Const(String[1])),
    WHTSVD: Const(Int32),
    M: Const(Int32),
    N: Const(Int32),
    F: Float64[LDF, Flat],
    LDF: Const(Int32),
    X: Float64[LDX, Flat],
    LDX: Const(Int32),
    Y: Float64[LDY, Flat],
    LDY: Const(Int32),
    NRNK: Const(Int32),
    TOL: Const(Float64),
    REIG: Float64[Flat],
    IMEIG: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Const(Int32),
    RES: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Const(Int32),
    V: Float64[LDV, Flat],
    LDV: Const(Int32),
    S: Float64[LDS, Flat],
    LDS: Const(Int32),
    WORK: Float64[Flat],
    LWORK: Const(Int32),
    IWORK: Int32[Flat],
    LIWORK: Const(Int32)
) -> tuple[Returns["X", Float64[LDX, Flat]], Returns["Y", Float64[LDY, Flat]], Int32, Returns["REIG", Float64[Flat]], Returns["IMEIG", Float64[Flat]], Returns["Z", Float64[LDZ, Flat]], Returns["RES", Float64[Flat]], Returns["B", Float64[LDB, Flat]], Returns["V", Float64[LDV, Flat]], Returns["S", Float64[LDS, Flat]], Returns["WORK", Float64[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("DGEEQU")
@external
def dgeequ(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEEQUB")
@external
def dgeequb(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEES")
@external
def dgees(
    JOBVS: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELECT: Addr(Bool),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    SDIM: Addr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VS: Float64[LDVS, Flat],
    LDVS: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEESX")
@external
def dgeesx(
    JOBVS: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELECT: Addr(Bool),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    SDIM: Addr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VS: Float64[LDVS, Flat],
    LDVS: Addr(Int32),
    RCONDE: Addr(Float64),
    RCONDV: Addr(Float64),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEEV")
@external
def dgeev(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEEVX")
@external
def dgeevx(
    BALANC: Addr(Const(String[1])),
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float64[Flat],
    ABNRM: Addr(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEHD2")
@external
def dgehd2(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEHRD")
@external
def dgehrd(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEJSV")
@external
def dgejsv(
    JOBA: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBT: Addr(Const(String[1])),
    JOBP: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    SVA: Float64[N],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    WORK: Float64[LWORK],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGELQ")
@external
def dgelq(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[Flat],
    TSIZE: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGELQ2")
@external
def dgelq2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGELQF")
@external
def dgelqf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGELQT")
@external
def dgelqt(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGELQT3")
@external
def dgelqt3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGELS")
@external
def dgels(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGELSD")
@external
def dgelsd(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    S: Float64[Flat],
    RCOND: Addr(Float64),
    RANK: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGELSS")
@external
def dgelss(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    S: Float64[Flat],
    RCOND: Addr(Float64),
    RANK: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGELST")
@external
def dgelst(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGELSY")
@external
def dgelsy(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    JPVT: Int32[Flat],
    RCOND: Addr(Float64),
    RANK: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEMLQ")
@external
def dgemlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[Flat],
    TSIZE: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEMLQT")
@external
def dgemlqt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEMQR")
@external
def dgemqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[Flat],
    TSIZE: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEMQRT")
@external
def dgemqrt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    NB: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQL2")
@external
def dgeql2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQLF")
@external
def dgeqlf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQP3")
@external
def dgeqp3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQP3RK")
@external
def dgeqp3rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    KMAX: Addr(Int32),
    ABSTOL: Addr(Float64),
    RELTOL: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    K: Addr(Int32),
    MAXC2NRMK: Addr(Float64),
    RELMAXC2NRMK: Addr(Float64),
    JPIV: Int32[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQR")
@external
def dgeqr(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[Flat],
    TSIZE: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQR2")
@external
def dgeqr2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQR2P")
@external
def dgeqr2p(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQRF")
@external
def dgeqrf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQRFP")
@external
def dgeqrfp(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQRT")
@external
def dgeqrt(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQRT2")
@external
def dgeqrt2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGEQRT3")
@external
def dgeqrt3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGERFS")
@external
def dgerfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGERFSX")
@external
def dgerfsx(
    TRANS: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGERQ2")
@external
def dgerq2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGERQF")
@external
def dgerqf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGESC2")
@external
def dgesc2(
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    RHS: Float64[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Addr(Float64)
) -> None: ...

@bind("DGESDD")
@external
def dgesdd(
    JOBZ: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGESV")
@external
def dgesv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGESVD")
@external
def dgesvd(
    JOBU: Addr(Const(String[1])),
    JOBVT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGESVDQ")
@external
def dgesvdq(
    JOBA: Addr(Const(String[1])),
    JOBP: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    NUMRANK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGESVDX")
@external
def dgesvdx(
    JOBU: Addr(Const(String[1])),
    JOBVT: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    NS: Addr(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGESVJ")
@external
def dgesvj(
    JOBA: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    SVA: Float64[N],
    MV: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    WORK: Float64[LWORK],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGESVX")
@external
def dgesvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGESVXX")
@external
def dgesvxx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    RPVGRW: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGETC2")
@external
def dgetc2(
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGETF2")
@external
def dgetf2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGETRF")
@external
def dgetrf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGETRF2")
@external
def dgetrf2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGETRI")
@external
def dgetri(
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGETRS")
@external
def dgetrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGETSLS")
@external
def dgetsls(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGETSQRHRT")
@external
def dgetsqrhrt(
    M: Addr(Int32),
    N: Addr(Int32),
    MB1: Addr(Int32),
    NB1: Addr(Int32),
    NB2: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGBAK")
@external
def dggbak(
    JOB: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    M: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGBAL")
@external
def dggbal(
    JOB: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGES")
@external
def dgges(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VSL: Float64[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Float64[LDVSR, Flat],
    LDVSR: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGES3")
@external
def dgges3(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VSL: Float64[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Float64[LDVSR, Flat],
    LDVSR: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGESX")
@external
def dggesx(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VSL: Float64[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Float64[LDVSR, Flat],
    LDVSR: Addr(Int32),
    RCONDE: Float64[2],
    RCONDV: Float64[2],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGEV")
@external
def dggev(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGEV3")
@external
def dggev3(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGEVX")
@external
def dggevx(
    BALANC: Addr(Const(String[1])),
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    ABNRM: Addr(Float64),
    BBNRM: Addr(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGGLM")
@external
def dggglm(
    N: Addr(Int32),
    M: Addr(Int32),
    P: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    D: Float64[Flat],
    X: Float64[Flat],
    Y: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGHD3")
@external
def dgghd3(
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGHRD")
@external
def dgghrd(
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGLSE")
@external
def dgglse(
    M: Addr(Int32),
    N: Addr(Int32),
    P: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    C: Float64[Flat],
    D: Float64[Flat],
    X: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGQRF")
@external
def dggqrf(
    N: Addr(Int32),
    M: Addr(Int32),
    P: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAUA: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    TAUB: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGRQF")
@external
def dggrqf(
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAUA: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    TAUB: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGSVD3")
@external
def dggsvd3(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    P: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGGSVP3")
@external
def dggsvp3(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    TOLA: Addr(Float64),
    TOLB: Addr(Float64),
    K: Addr(Int32),
    L: Addr(Int32),
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    IWORK: Int32[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGSVJ0")
@external
def dgsvj0(
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[N],
    SVA: Float64[N],
    MV: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    EPS: Addr(Float64),
    SFMIN: Addr(Float64),
    TOL: Addr(Float64),
    NSWEEP: Addr(Int32),
    WORK: Float64[LWORK],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGSVJ1")
@external
def dgsvj1(
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[N],
    SVA: Float64[N],
    MV: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    EPS: Addr(Float64),
    SFMIN: Addr(Float64),
    TOL: Addr(Float64),
    NSWEEP: Addr(Int32),
    WORK: Float64[LWORK],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGTCON")
@external
def dgtcon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGTRFS")
@external
def dgtrfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DLF: Float64[Flat],
    DF: Float64[Flat],
    DUF: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGTSV")
@external
def dgtsv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGTSVX")
@external
def dgtsvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DLF: Float64[Flat],
    DF: Float64[Flat],
    DUF: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGTTRF")
@external
def dgttrf(
    N: Addr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DGTTRS")
@external
def dgttrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DGTTS2")
@external
def dgtts2(
    ITRANS: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("DHGEQZ")
@external
def dhgeqz(
    JOB: Addr(Const(String[1])),
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DHSEIN")
@external
def dhsein(
    SIDE: Addr(Const(String[1])),
    EIGSRC: Addr(Const(String[1])),
    INITV: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float64[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DHSEQR")
@external
def dhseqr(
    JOB: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DISNAN")
@external
@native_call([Addr(Arg(0))])
def disnan(
    DIN: Const(Float64)
) -> Bool: ...

@bind("DLA_GBAMV")
@external
def dla_gbamv(
    TRANS: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    ALPHA: Addr(Float64),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float64),
    Y: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("DLA_GBRCOND")
@external
def dla_gbrcond(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    CMODE: Addr(Int32),
    C: Float64[Flat],
    INFO: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_GBRFSX_EXTENDED")
@external
def dla_gbrfsx_extended(
    PREC_TYPE: Addr(Int32),
    TRANS_TYPE: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    Y: Float64[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Addr(Float64),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float64),
    DZ_UB: Addr(Float64),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLA_GBRPVGRW")
@external
def dla_gbrpvgrw(
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NCOLS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Addr(Int32)
) -> Float64: ...

@bind("DLA_GEAMV")
@external
def dla_geamv(
    TRANS: Addr(Int32),
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

@bind("DLA_GERCOND")
@external
def dla_gercond(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    CMODE: Addr(Int32),
    C: Float64[Flat],
    INFO: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_GERFSX_EXTENDED")
@external
def dla_gerfsx_extended(
    PREC_TYPE: Addr(Int32),
    TRANS_TYPE: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    Y: Float64[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Addr(Int32),
    ERRS_N: Float64[NRHS, Flat],
    ERRS_C: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Addr(Float64),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float64),
    DZ_UB: Addr(Float64),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLA_GERPVGRW")
@external
def dla_gerpvgrw(
    N: Addr(Int32),
    NCOLS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32)
) -> Float64: ...

@bind("DLA_LIN_BERR")
@external
def dla_lin_berr(
    N: Addr(Int32),
    NZ: Addr(Int32),
    NRHS: Addr(Int32),
    RES: Annotated[Float64[N, NRHS], ORDER_F],
    AYB: Annotated[Float64[N, NRHS], ORDER_F],
    BERR: Float64[NRHS]
) -> None: ...

@bind("DLA_PORCOND")
@external
def dla_porcond(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    CMODE: Addr(Int32),
    C: Float64[Flat],
    INFO: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_PORFSX_EXTENDED")
@external
def dla_porfsx_extended(
    PREC_TYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    COLEQU: Addr(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    Y: Float64[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Addr(Float64),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float64),
    DZ_UB: Addr(Float64),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLA_PORPVGRW")
@external
def dla_porpvgrw(
    UPLO: Addr(Const(String[1])),
    NCOLS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLA_SYAMV")
@external
def dla_syamv(
    UPLO: Addr(Int32),
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

@bind("DLA_SYRCOND")
@external
def dla_syrcond(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    CMODE: Addr(Int32),
    C: Float64[Flat],
    INFO: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_SYRFSX_EXTENDED")
@external
def dla_syrfsx_extended(
    PREC_TYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    Y: Float64[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Addr(Float64),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float64),
    DZ_UB: Addr(Float64),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLA_SYRPVGRW")
@external
def dla_syrpvgrw(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    INFO: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLA_WWADDW")
@external
def dla_wwaddw(
    N: Addr(Int32),
    X: Float64[Flat],
    Y: Float64[Flat],
    W: Float64[Flat]
) -> None: ...

@bind("DLABAD")
@external
def dlabad(
    SMALL: Addr(Float64),
    LARGE: Addr(Float64)
) -> None: ...

@bind("DLABRD")
@external
def dlabrd(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Float64[Flat],
    TAUP: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    Y: Float64[LDY, Flat],
    LDY: Addr(Int32)
) -> None: ...

@bind("DLACN2")
@external
def dlacn2(
    N: Addr(Int32),
    V: Float64[Flat],
    X: Float64[Flat],
    ISGN: Int32[Flat],
    EST: Addr(Float64),
    KASE: Addr(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("DLACON")
@external
def dlacon(
    N: Addr(Int32),
    V: Float64[Flat],
    X: Float64[Flat],
    ISGN: Int32[Flat],
    EST: Addr(Float64),
    KASE: Addr(Int32)
) -> None: ...

@bind("DLACPY")
@external
def dlacpy(
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("DLADIV")
@external
def dladiv(
    A: Addr(Float64),
    B: Addr(Float64),
    C: Addr(Float64),
    D: Addr(Float64),
    P: Addr(Float64),
    Q: Addr(Float64)
) -> None: ...

@bind("DLADIV1")
@external
def dladiv1(
    A: Addr(Float64),
    B: Addr(Float64),
    C: Addr(Float64),
    D: Addr(Float64),
    P: Addr(Float64),
    Q: Addr(Float64)
) -> None: ...

@bind("DLADIV2")
@external
def dladiv2(
    A: Addr(Float64),
    B: Addr(Float64),
    C: Addr(Float64),
    D: Addr(Float64),
    R: Addr(Float64),
    T: Addr(Float64)
) -> Float64: ...

@bind("DLAE2")
@external
def dlae2(
    A: Addr(Float64),
    B: Addr(Float64),
    C: Addr(Float64),
    RT1: Addr(Float64),
    RT2: Addr(Float64)
) -> None: ...

@bind("DLAEBZ")
@external
def dlaebz(
    IJOB: Addr(Int32),
    NITMAX: Addr(Int32),
    N: Addr(Int32),
    MMAX: Addr(Int32),
    MINP: Addr(Int32),
    NBMIN: Addr(Int32),
    ABSTOL: Addr(Float64),
    RELTOL: Addr(Float64),
    PIVMIN: Addr(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    NVAL: Int32[Flat],
    AB: Float64[MMAX, Flat],
    C: Float64[Flat],
    MOUT: Addr(Int32),
    NAB: Int32[MMAX, Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAED0")
@external
def dlaed0(
    ICOMPQ: Addr(Int32),
    QSIZ: Addr(Int32),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    QSTORE: Float64[LDQS, Flat],
    LDQS: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAED1")
@external
def dlaed1(
    N: Addr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    INDXQ: Int32[Flat],
    RHO: Addr(Float64),
    CUTPNT: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAED2")
@external
def dlaed2(
    K: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    INDXQ: Int32[Flat],
    RHO: Addr(Float64),
    Z: Float64[Flat],
    DLAMBDA: Float64[Flat],
    W: Float64[Flat],
    Q2: Float64[Flat],
    INDX: Int32[Flat],
    INDXC: Int32[Flat],
    INDXP: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAED3")
@external
def dlaed3(
    K: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    RHO: Addr(Float64),
    DLAMBDA: Float64[Flat],
    Q2: Float64[Flat],
    INDX: Int32[Flat],
    CTOT: Int32[Flat],
    W: Float64[Flat],
    S: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAED4")
@external
def dlaed4(
    N: Addr(Int32),
    I: Addr(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    DELTA: Float64[Flat],
    RHO: Addr(Float64),
    DLAM: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAED5")
@external
def dlaed5(
    I: Addr(Int32),
    D: Float64[2],
    Z: Float64[2],
    DELTA: Float64[2],
    RHO: Addr(Float64),
    DLAM: Addr(Float64)
) -> None: ...

@bind("DLAED6")
@external
def dlaed6(
    KNITER: Addr(Int32),
    ORGATI: Addr(Bool),
    RHO: Addr(Float64),
    D: Float64[3],
    Z: Float64[3],
    FINIT: Addr(Float64),
    TAU: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAED7")
@external
def dlaed7(
    ICOMPQ: Addr(Int32),
    N: Addr(Int32),
    QSIZ: Addr(Int32),
    TLVLS: Addr(Int32),
    CURLVL: Addr(Int32),
    CURPBM: Addr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    INDXQ: Int32[Flat],
    RHO: Addr(Float64),
    CUTPNT: Addr(Int32),
    QSTORE: Float64[Flat],
    QPTR: Int32[Flat],
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAED8")
@external
def dlaed8(
    ICOMPQ: Addr(Int32),
    K: Addr(Int32),
    N: Addr(Int32),
    QSIZ: Addr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    INDXQ: Int32[Flat],
    RHO: Addr(Float64),
    CUTPNT: Addr(Int32),
    Z: Float64[Flat],
    DLAMBDA: Float64[Flat],
    Q2: Float64[LDQ2, Flat],
    LDQ2: Addr(Int32),
    W: Float64[Flat],
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAED9")
@external
def dlaed9(
    K: Addr(Int32),
    KSTART: Addr(Int32),
    KSTOP: Addr(Int32),
    N: Addr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    RHO: Addr(Float64),
    DLAMBDA: Float64[Flat],
    W: Float64[Flat],
    S: Float64[LDS, Flat],
    LDS: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAEDA")
@external
def dlaeda(
    N: Addr(Int32),
    TLVLS: Addr(Int32),
    CURLVL: Addr(Int32),
    CURPBM: Addr(Int32),
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    Q: Float64[Flat],
    QPTR: Int32[Flat],
    Z: Float64[Flat],
    ZTEMP: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAEIN")
@external
def dlaein(
    RIGHTV: Addr(Bool),
    NOINIT: Addr(Bool),
    N: Addr(Int32),
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    WR: Addr(Float64),
    WI: Addr(Float64),
    VR: Float64[Flat],
    VI: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    EPS3: Addr(Float64),
    SMLNUM: Addr(Float64),
    BIGNUM: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAEV2")
@external
def dlaev2(
    A: Addr(Float64),
    B: Addr(Float64),
    C: Addr(Float64),
    RT1: Addr(Float64),
    RT2: Addr(Float64),
    CS1: Addr(Float64),
    SN1: Addr(Float64)
) -> None: ...

@bind("DLAEXC")
@external
def dlaexc(
    WANTQ: Addr(Bool),
    N: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    J1: Addr(Int32),
    N1: Addr(Int32),
    N2: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAG2")
@external
def dlag2(
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    SAFMIN: Addr(Float64),
    SCALE1: Addr(Float64),
    SCALE2: Addr(Float64),
    WR1: Addr(Float64),
    WR2: Addr(Float64),
    WI: Addr(Float64)
) -> None: ...

@bind("DLAG2S")
@external
def dlag2s(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    SA: Float32[LDSA, Flat],
    LDSA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAGS2")
@external
def dlags2(
    UPPER: Addr(Bool),
    A1: Addr(Float64),
    A2: Addr(Float64),
    A3: Addr(Float64),
    B1: Addr(Float64),
    B2: Addr(Float64),
    B3: Addr(Float64),
    CSU: Addr(Float64),
    SNU: Addr(Float64),
    CSV: Addr(Float64),
    SNV: Addr(Float64),
    CSQ: Addr(Float64),
    SNQ: Addr(Float64)
) -> None: ...

@bind("DLAGTF")
@external
def dlagtf(
    N: Addr(Int32),
    A: Float64[Flat],
    LAMBDA: Addr(Float64),
    B: Float64[Flat],
    C: Float64[Flat],
    TOL: Addr(Float64),
    D: Float64[Flat],
    IN: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAGTM")
@external
def dlagtm(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    ALPHA: Addr(Float64),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    BETA: Addr(Float64),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("DLAGTS")
@external
def dlagts(
    JOB: Addr(Int32),
    N: Addr(Int32),
    A: Float64[Flat],
    B: Float64[Flat],
    C: Float64[Flat],
    D: Float64[Flat],
    IN: Int32[Flat],
    Y: Float64[Flat],
    TOL: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAGV2")
@external
def dlagv2(
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHAR: Float64[2],
    ALPHAI: Float64[2],
    BETA: Float64[2],
    CSL: Addr(Float64),
    SNL: Addr(Float64),
    CSR: Addr(Float64),
    SNR: Addr(Float64)
) -> None: ...

@bind("DLAHQR")
@external
def dlahqr(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAHR2")
@external
def dlahr2(
    N: Addr(Int32),
    K: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[NB],
    T: Annotated[Float64[LDT, NB], ORDER_F],
    LDT: Addr(Int32),
    Y: Annotated[Float64[LDY, NB], ORDER_F],
    LDY: Addr(Int32)
) -> None: ...

@bind("DLAIC1")
@external
def dlaic1(
    JOB: Addr(Int32),
    J: Addr(Int32),
    X: Float64[J],
    SEST: Addr(Float64),
    W: Float64[J],
    GAMMA: Addr(Float64),
    SESTPR: Addr(Float64),
    S: Addr(Float64),
    C: Addr(Float64)
) -> None: ...

@bind("DLAISNAN")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1))])
def dlaisnan(
    DIN1: Const(Float64),
    DIN2: Const(Float64)
) -> Bool: ...

@bind("DLALN2")
@external
def dlaln2(
    LTRANS: Addr(Bool),
    NA: Addr(Int32),
    NW: Addr(Int32),
    SMIN: Addr(Float64),
    CA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D1: Addr(Float64),
    D2: Addr(Float64),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WR: Addr(Float64),
    WI: Addr(Float64),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    SCALE: Addr(Float64),
    XNORM: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLALS0")
@external
def dlals0(
    ICOMPQ: Addr(Int32),
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    NRHS: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    BX: Float64[LDBX, Flat],
    LDBX: Addr(Int32),
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Addr(Int32),
    POLES: Float64[LDGNUM, Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[LDGNUM, Flat],
    Z: Float64[Flat],
    K: Addr(Int32),
    C: Addr(Float64),
    S: Addr(Float64),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLALSA")
@external
def dlalsa(
    ICOMPQ: Addr(Int32),
    SMLSIZ: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    BX: Float64[LDBX, Flat],
    LDBX: Addr(Int32),
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float64[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float64[LDU, Flat],
    DIFR: Float64[LDU, Flat],
    Z: Float64[LDU, Flat],
    POLES: Float64[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float64[LDU, Flat],
    C: Float64[Flat],
    S: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLALSD")
@external
def dlalsd(
    UPLO: Addr(Const(String[1])),
    SMLSIZ: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    RCOND: Addr(Float64),
    RANK: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAMRG")
@external
def dlamrg(
    N1: Addr(Int32),
    N2: Addr(Int32),
    A: Float64[Flat],
    DTRD1: Addr(Int32),
    DTRD2: Addr(Int32),
    INDEX: Int32[Flat]
) -> None: ...

@bind("DLAMSWLQ")
@external
def dlamswlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAMTSQR")
@external
def dlamtsqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLANEG")
@external
def dlaneg(
    N: Addr(Int32),
    D: Float64[Flat],
    LLD: Float64[Flat],
    SIGMA: Addr(Float64),
    PIVMIN: Addr(Float64),
    R: Addr(Int32)
) -> Int32: ...

@bind("DLANGB")
@external
def dlangb(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANGE")
@external
def dlange(
    NORM: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANGT")
@external
def dlangt(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat]
) -> Float64: ...

@bind("DLANHS")
@external
def dlanhs(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANSB")
@external
def dlansb(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANSF")
@external
def dlansf(
    NORM: Addr(Const(String[1])),
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    WORK: Annotated[Float64[Flat], SourceDims("0:*")]
) -> Float64: ...

@bind("DLANSP")
@external
def dlansp(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANST")
@external
def dlanst(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat]
) -> Float64: ...

@bind("DLANSY")
@external
def dlansy(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANTB")
@external
def dlantb(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANTP")
@external
def dlantp(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANTR")
@external
def dlantr(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANV2")
@external
def dlanv2(
    A: Addr(Float64),
    B: Addr(Float64),
    C: Addr(Float64),
    D: Addr(Float64),
    RT1R: Addr(Float64),
    RT1I: Addr(Float64),
    RT2R: Addr(Float64),
    RT2I: Addr(Float64),
    CS: Addr(Float64),
    SN: Addr(Float64)
) -> None: ...

@bind("DLAORHR_COL_GETRFNP")
@external
def dlaorhr_col_getrfnp(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAORHR_COL_GETRFNP2")
@external
def dlaorhr_col_getrfnp2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAPLL")
@external
def dlapll(
    N: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32),
    Y: Float64[Flat],
    INCY: Addr(Int32),
    SSMIN: Addr(Float64)
) -> None: ...

@bind("DLAPMR")
@external
def dlapmr(
    FORWRD: Addr(Bool),
    M: Addr(Int32),
    N: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("DLAPMT")
@external
def dlapmt(
    FORWRD: Addr(Bool),
    M: Addr(Int32),
    N: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("DLAPY2")
@external
def dlapy2(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("DLAPY3")
@external
def dlapy3(
    X: Addr(Float64),
    Y: Addr(Float64),
    Z: Addr(Float64)
) -> Float64: ...

@bind("DLAQGB")
@external
def dlaqgb(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("DLAQGE")
@external
def dlaqge(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("DLAQP2")
@external
def dlaqp2(
    M: Addr(Int32),
    N: Addr(Int32),
    OFFSET: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Float64[Flat]
) -> None: ...

@bind("DLAQP2RK")
@external
def dlaqp2rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    IOFFSET: Addr(Int32),
    KMAX: Addr(Int32),
    ABSTOL: Addr(Float64),
    RELTOL: Addr(Float64),
    KP1: Addr(Int32),
    MAXC2NRM: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    K: Addr(Int32),
    MAXC2NRMK: Addr(Float64),
    RELMAXC2NRMK: Addr(Float64),
    JPIV: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAQP3RK")
@external
def dlaqp3rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    IOFFSET: Addr(Int32),
    NB: Addr(Int32),
    ABSTOL: Addr(Float64),
    RELTOL: Addr(Float64),
    KP1: Addr(Int32),
    MAXC2NRM: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    DONE: Addr(Bool),
    KB: Addr(Int32),
    MAXC2NRMK: Addr(Float64),
    RELMAXC2NRMK: Addr(Float64),
    JPIV: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Float64[Flat],
    F: Float64[LDF, Flat],
    LDF: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAQPS")
@external
def dlaqps(
    M: Addr(Int32),
    N: Addr(Int32),
    OFFSET: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Float64[Flat],
    F: Float64[LDF, Flat],
    LDF: Addr(Int32)
) -> None: ...

@bind("DLAQR0")
@external
def dlaqr0(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAQR1")
@external
def dlaqr1(
    N: Addr(Int32),
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    SR1: Addr(Float64),
    SI1: Addr(Float64),
    SR2: Addr(Float64),
    SI2: Addr(Float64),
    V: Float64[Flat]
) -> None: ...

@bind("DLAQR2")
@external
def dlaqr2(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NW: Addr(Int32),
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    NS: Addr(Int32),
    ND: Addr(Int32),
    SR: Float64[Flat],
    SI: Float64[Flat],
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    NH: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    NV: Addr(Int32),
    WV: Float64[LDWV, Flat],
    LDWV: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32)
) -> None: ...

@bind("DLAQR3")
@external
def dlaqr3(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NW: Addr(Int32),
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    NS: Addr(Int32),
    ND: Addr(Int32),
    SR: Float64[Flat],
    SI: Float64[Flat],
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    NH: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    NV: Addr(Int32),
    WV: Float64[LDWV, Flat],
    LDWV: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32)
) -> None: ...

@bind("DLAQR4")
@external
def dlaqr4(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAQR5")
@external
def dlaqr5(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    KACC22: Addr(Int32),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NSHFTS: Addr(Int32),
    SR: Float64[Flat],
    SI: Float64[Flat],
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    NV: Addr(Int32),
    WV: Float64[LDWV, Flat],
    LDWV: Addr(Int32),
    NH: Addr(Int32),
    WH: Float64[LDWH, Flat],
    LDWH: Addr(Int32)
) -> None: ...

@bind("DLAQSB")
@external
def dlaqsb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("DLAQSP")
@external
def dlaqsp(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("DLAQSY")
@external
def dlaqsy(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("DLAQTR")
@external
def dlaqtr(
    LTRAN: Addr(Bool),
    LREAL: Addr(Bool),
    N: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    B: Float64[Flat],
    W: Addr(Float64),
    SCALE: Addr(Float64),
    X: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Arg(10), Arg(11), Arg(12), Arg(13), Addr(Arg(14)), Arg(15), Addr(Arg(16)), Arg(17), Addr(Arg(18)), Addr(Arg(19)), Return('INFO', 0)])
def dlaqz0(
    WANTS: Addr(Const(String[1])),
    WANTQ: Addr(Const(String[1])),
    WANTZ: Addr(Const(String[1])),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    A: Float64[LDA, Flat],
    LDA: Const(Int32),
    B: Float64[LDB, Flat],
    LDB: Const(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Const(Int32),
    WORK: Float64[Flat],
    LWORK: Const(Int32),
    REC: Const(Int32)
) -> Int32: ...

@bind("DLAQZ1")
@external
@native_call([Arg(0), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Addr(Arg(7)), Addr(Arg(8)), Arg(9)])
def dlaqz1(
    A: Const(Float64[LDA, Flat]),
    LDA: Const(Int32),
    B: Const(Float64[LDB, Flat]),
    LDB: Const(Int32),
    SR1: Const(Float64),
    SR2: Const(Float64),
    SI: Const(Float64),
    BETA1: Const(Float64),
    BETA2: Const(Float64),
    V: Float64[Flat]
) -> Returns["V", Float64[Flat]]: ...

@bind("DLAQZ2")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Addr(Arg(11)), Arg(12), Addr(Arg(13)), Addr(Arg(14)), Addr(Arg(15)), Arg(16), Addr(Arg(17))])
def dlaqz2(
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    K: Const(Int32),
    ISTARTM: Const(Int32),
    ISTOPM: Const(Int32),
    IHI: Const(Int32),
    A: Float64[LDA, Flat],
    LDA: Const(Int32),
    B: Float64[LDB, Flat],
    LDB: Const(Int32),
    NQ: Const(Int32),
    QSTART: Const(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Const(Int32),
    NZ: Const(Int32),
    ZSTART: Const(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Const(Int32)
) -> None: ...

@bind("DLAQZ3")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Arg(11), Addr(Arg(12)), Arg(13), Addr(Arg(14)), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Arg(18), Addr(Arg(19)), Arg(20), Addr(Arg(21)), Arg(22), Addr(Arg(23)), Addr(Arg(24)), Return('INFO', 2)])
def dlaqz3(
    ILSCHUR: Const(Bool),
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    NW: Const(Int32),
    A: Float64[LDA, Flat],
    LDA: Const(Int32),
    B: Float64[LDB, Flat],
    LDB: Const(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Const(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    QC: Float64[LDQC, Flat],
    LDQC: Const(Int32),
    ZC: Float64[LDZC, Flat],
    LDZC: Const(Int32),
    WORK: Float64[Flat],
    LWORK: Const(Int32),
    REC: Const(Int32)
) -> tuple[Int32, Int32, Int32]: ...

@bind("DLAQZ4")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Arg(9), Arg(10), Arg(11), Addr(Arg(12)), Arg(13), Addr(Arg(14)), Arg(15), Addr(Arg(16)), Arg(17), Addr(Arg(18)), Arg(19), Addr(Arg(20)), Arg(21), Addr(Arg(22)), Arg(23), Addr(Arg(24)), Return('INFO', 0)])
def dlaqz4(
    ILSCHUR: Const(Bool),
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    NSHIFTS: Const(Int32),
    NBLOCK_DESIRED: Const(Int32),
    SR: Float64[Flat],
    SI: Float64[Flat],
    SS: Float64[Flat],
    A: Float64[LDA, Flat],
    LDA: Const(Int32),
    B: Float64[LDB, Flat],
    LDB: Const(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Const(Int32),
    QC: Float64[LDQC, Flat],
    LDQC: Const(Int32),
    ZC: Float64[LDZC, Flat],
    LDZC: Const(Int32),
    WORK: Float64[Flat],
    LWORK: Const(Int32)
) -> Int32: ...

@bind("DLAR1V")
@external
def dlar1v(
    N: Addr(Int32),
    B1: Addr(Int32),
    BN: Addr(Int32),
    LAMBDA: Addr(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    LD: Float64[Flat],
    LLD: Float64[Flat],
    PIVMIN: Addr(Float64),
    GAPTOL: Addr(Float64),
    Z: Float64[Flat],
    WANTNC: Addr(Bool),
    NEGCNT: Addr(Int32),
    ZTZ: Addr(Float64),
    MINGMA: Addr(Float64),
    R: Addr(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Addr(Float64),
    RESID: Addr(Float64),
    RQCORR: Addr(Float64),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLAR2V")
@external
def dlar2v(
    N: Addr(Int32),
    X: Float64[Flat],
    Y: Float64[Flat],
    Z: Float64[Flat],
    INCX: Addr(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("DLARF")
@external
def dlarf(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Float64[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARF1F")
@external
def dlarf1f(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Float64[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARF1L")
@external
def dlarf1l(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Float64[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARFB")
@external
def dlarfb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("DLARFB_GETT")
@external
def dlarfb_gett(
    IDENT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("DLARFG")
@external
def dlarfg(
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    X: Float64[Flat],
    INCX: Addr(Int32),
    TAU: Addr(Float64)
) -> None: ...

@bind("DLARFGP")
@external
def dlarfgp(
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    X: Float64[Flat],
    INCX: Addr(Int32),
    TAU: Addr(Float64)
) -> None: ...

@bind("DLARFT")
@external
def dlarft(
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    TAU: Float64[Flat],
    T: Float64[LDT, Flat],
    LDT: Addr(Int32)
) -> None: ...

@bind("DLARFX")
@external
def dlarfx(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Float64[Flat],
    TAU: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARFY")
@external
def dlarfy(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    V: Float64[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARGV")
@external
def dlargv(
    N: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32),
    Y: Float64[Flat],
    INCY: Addr(Int32),
    C: Float64[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("DLARMM")
@external
def dlarmm(
    ANORM: Addr(Float64),
    BNORM: Addr(Float64),
    CNORM: Addr(Float64)
) -> Float64: ...

@bind("DLARNV")
@external
def dlarnv(
    IDIST: Addr(Int32),
    ISEED: Int32[4],
    N: Addr(Int32),
    X: Float64[Flat]
) -> None: ...

@bind("DLARRA")
@external
def dlarra(
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    SPLTOL: Addr(Float64),
    TNRM: Addr(Float64),
    NSPLIT: Addr(Int32),
    ISPLIT: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLARRB")
@external
def dlarrb(
    N: Addr(Int32),
    D: Float64[Flat],
    LLD: Float64[Flat],
    IFIRST: Addr(Int32),
    ILAST: Addr(Int32),
    RTOL1: Addr(Float64),
    RTOL2: Addr(Float64),
    OFFSET: Addr(Int32),
    W: Float64[Flat],
    WGAP: Float64[Flat],
    WERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Addr(Float64),
    SPDIAM: Addr(Float64),
    TWIST: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLARRC")
@external
def dlarrc(
    JOBT: Addr(Const(String[1])),
    N: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    PIVMIN: Addr(Float64),
    EIGCNT: Addr(Int32),
    LCNT: Addr(Int32),
    RCNT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLARRD")
@external
def dlarrd(
    RANGE: Addr(Const(String[1])),
    ORDER: Addr(Const(String[1])),
    N: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    GERS: Float64[Flat],
    RELTOL: Addr(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    PIVMIN: Addr(Float64),
    NSPLIT: Addr(Int32),
    ISPLIT: Int32[Flat],
    M: Addr(Int32),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WL: Addr(Float64),
    WU: Addr(Float64),
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLARRE")
@external
def dlarre(
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    RTOL1: Addr(Float64),
    RTOL2: Addr(Float64),
    SPLTOL: Addr(Float64),
    NSPLIT: Addr(Int32),
    ISPLIT: Int32[Flat],
    M: Addr(Int32),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WGAP: Float64[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float64[Flat],
    PIVMIN: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLARRF")
@external
def dlarrf(
    N: Addr(Int32),
    D: Float64[Flat],
    L: Float64[Flat],
    LD: Float64[Flat],
    CLSTRT: Addr(Int32),
    CLEND: Addr(Int32),
    W: Float64[Flat],
    WGAP: Float64[Flat],
    WERR: Float64[Flat],
    SPDIAM: Addr(Float64),
    CLGAPL: Addr(Float64),
    CLGAPR: Addr(Float64),
    PIVMIN: Addr(Float64),
    SIGMA: Addr(Float64),
    DPLUS: Float64[Flat],
    LPLUS: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLARRJ")
@external
def dlarrj(
    N: Addr(Int32),
    D: Float64[Flat],
    E2: Float64[Flat],
    IFIRST: Addr(Int32),
    ILAST: Addr(Int32),
    RTOL: Addr(Float64),
    OFFSET: Addr(Int32),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Addr(Float64),
    SPDIAM: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLARRK")
@external
def dlarrk(
    N: Addr(Int32),
    IW: Addr(Int32),
    GL: Addr(Float64),
    GU: Addr(Float64),
    D: Float64[Flat],
    E2: Float64[Flat],
    PIVMIN: Addr(Float64),
    RELTOL: Addr(Float64),
    W: Addr(Float64),
    WERR: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLARRR")
@external
def dlarrr(
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLARRV")
@external
def dlarrv(
    N: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    PIVMIN: Addr(Float64),
    ISPLIT: Int32[Flat],
    M: Addr(Int32),
    DOL: Addr(Int32),
    DOU: Addr(Int32),
    MINRGP: Addr(Float64),
    RTOL1: Addr(Float64),
    RTOL2: Addr(Float64),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WGAP: Float64[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLARSCL2")
@external
def dlarscl2(
    M: Addr(Int32),
    N: Addr(Int32),
    D: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Addr(Int32)
) -> None: ...

@bind("DLARTG")
@external
def dlartg(
    f: Addr(Float64),
    g: Addr(Float64),
    c: Addr(Float64),
    s: Addr(Float64),
    r: Addr(Float64)
) -> None: ...

@bind("DLARTGP")
@external
def dlartgp(
    F: Addr(Float64),
    G: Addr(Float64),
    CS: Addr(Float64),
    SN: Addr(Float64),
    R: Addr(Float64)
) -> None: ...

@bind("DLARTGS")
@external
def dlartgs(
    X: Addr(Float64),
    Y: Addr(Float64),
    SIGMA: Addr(Float64),
    CS: Addr(Float64),
    SN: Addr(Float64)
) -> None: ...

@bind("DLARTV")
@external
def dlartv(
    N: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32),
    Y: Float64[Flat],
    INCY: Addr(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("DLARUV")
@external
def dlaruv(
    ISEED: Int32[4],
    N: Addr(Int32),
    X: Float64[N]
) -> None: ...

@bind("DLARZ")
@external
def dlarz(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    V: Float64[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARZB")
@external
def dlarzb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("DLARZT")
@external
def dlarzt(
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    TAU: Float64[Flat],
    T: Float64[LDT, Flat],
    LDT: Addr(Int32)
) -> None: ...

@bind("DLAS2")
@external
def dlas2(
    F: Addr(Float64),
    G: Addr(Float64),
    H: Addr(Float64),
    SSMIN: Addr(Float64),
    SSMAX: Addr(Float64)
) -> None: ...

@bind("DLASCL")
@external
def dlascl(
    TYPE: Addr(Const(String[1])),
    KL: Addr(Int32),
    KU: Addr(Int32),
    CFROM: Addr(Float64),
    CTO: Addr(Float64),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASCL2")
@external
def dlascl2(
    M: Addr(Int32),
    N: Addr(Int32),
    D: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Addr(Int32)
) -> None: ...

@bind("DLASD0")
@external
def dlasd0(
    N: Addr(Int32),
    SQRE: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Addr(Int32),
    SMLSIZ: Addr(Int32),
    IWORK: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASD1")
@external
def dlasd1(
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    D: Float64[Flat],
    ALPHA: Addr(Float64),
    BETA: Addr(Float64),
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Addr(Int32),
    IDXQ: Int32[Flat],
    IWORK: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASD2")
@external
def dlasd2(
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    K: Addr(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    ALPHA: Addr(Float64),
    BETA: Addr(Float64),
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Addr(Int32),
    DSIGMA: Float64[Flat],
    U2: Float64[LDU2, Flat],
    LDU2: Addr(Int32),
    VT2: Float64[LDVT2, Flat],
    LDVT2: Addr(Int32),
    IDXP: Int32[Flat],
    IDX: Int32[Flat],
    IDXC: Int32[Flat],
    IDXQ: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASD3")
@external
def dlasd3(
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    K: Addr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    DSIGMA: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Addr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Addr(Int32),
    VT2: Float64[LDVT2, Flat],
    LDVT2: Addr(Int32),
    IDXC: Int32[Flat],
    CTOT: Int32[Flat],
    Z: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASD4")
@external
def dlasd4(
    N: Addr(Int32),
    I: Addr(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    DELTA: Float64[Flat],
    RHO: Addr(Float64),
    SIGMA: Addr(Float64),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASD5")
@external
def dlasd5(
    I: Addr(Int32),
    D: Float64[2],
    Z: Float64[2],
    DELTA: Float64[2],
    RHO: Addr(Float64),
    DSIGMA: Addr(Float64),
    WORK: Float64[2]
) -> None: ...

@bind("DLASD6")
@external
def dlasd6(
    ICOMPQ: Addr(Int32),
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    D: Float64[Flat],
    VF: Float64[Flat],
    VL: Float64[Flat],
    ALPHA: Addr(Float64),
    BETA: Addr(Float64),
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Addr(Int32),
    POLES: Float64[LDGNUM, Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[Flat],
    Z: Float64[Flat],
    K: Addr(Int32),
    C: Addr(Float64),
    S: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASD7")
@external
def dlasd7(
    ICOMPQ: Addr(Int32),
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    K: Addr(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    ZW: Float64[Flat],
    VF: Float64[Flat],
    VFW: Float64[Flat],
    VL: Float64[Flat],
    VLW: Float64[Flat],
    ALPHA: Addr(Float64),
    BETA: Addr(Float64),
    DSIGMA: Float64[Flat],
    IDX: Int32[Flat],
    IDXP: Int32[Flat],
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Addr(Int32),
    C: Addr(Float64),
    S: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASD8")
@external
def dlasd8(
    ICOMPQ: Addr(Int32),
    K: Addr(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    VF: Float64[Flat],
    VL: Float64[Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[LDDIFR, Flat],
    LDDIFR: Addr(Int32),
    DSIGMA: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASDA")
@external
def dlasda(
    ICOMPQ: Addr(Int32),
    SMLSIZ: Addr(Int32),
    N: Addr(Int32),
    SQRE: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float64[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float64[LDU, Flat],
    DIFR: Float64[LDU, Flat],
    Z: Float64[LDU, Flat],
    POLES: Float64[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float64[LDU, Flat],
    C: Float64[Flat],
    S: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASDQ")
@external
def dlasdq(
    UPLO: Addr(Const(String[1])),
    SQRE: Addr(Int32),
    N: Addr(Int32),
    NCVT: Addr(Int32),
    NRU: Addr(Int32),
    NCC: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VT: Float64[LDVT, Flat],
    LDVT: Addr(Int32),
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASDT")
@external
def dlasdt(
    N: Addr(Int32),
    LVL: Addr(Int32),
    ND: Addr(Int32),
    INODE: Int32[Flat],
    NDIML: Int32[Flat],
    NDIMR: Int32[Flat],
    MSUB: Addr(Int32)
) -> None: ...

@bind("DLASET")
@external
def dlaset(
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    BETA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("DLASQ1")
@external
def dlasq1(
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASQ2")
@external
def dlasq2(
    N: Addr(Int32),
    Z: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASQ3")
@external
def dlasq3(
    I0: Addr(Int32),
    N0: Addr(Int32),
    Z: Float64[Flat],
    PP: Addr(Int32),
    DMIN: Addr(Float64),
    SIGMA: Addr(Float64),
    DESIG: Addr(Float64),
    QMAX: Addr(Float64),
    NFAIL: Addr(Int32),
    ITER: Addr(Int32),
    NDIV: Addr(Int32),
    IEEE: Addr(Bool),
    TTYPE: Addr(Int32),
    DMIN1: Addr(Float64),
    DMIN2: Addr(Float64),
    DN: Addr(Float64),
    DN1: Addr(Float64),
    DN2: Addr(Float64),
    G: Addr(Float64),
    TAU: Addr(Float64)
) -> None: ...

@bind("DLASQ4")
@external
def dlasq4(
    I0: Addr(Int32),
    N0: Addr(Int32),
    Z: Float64[Flat],
    PP: Addr(Int32),
    N0IN: Addr(Int32),
    DMIN: Addr(Float64),
    DMIN1: Addr(Float64),
    DMIN2: Addr(Float64),
    DN: Addr(Float64),
    DN1: Addr(Float64),
    DN2: Addr(Float64),
    TAU: Addr(Float64),
    TTYPE: Addr(Int32),
    G: Addr(Float64)
) -> None: ...

@bind("DLASQ5")
@external
def dlasq5(
    I0: Addr(Int32),
    N0: Addr(Int32),
    Z: Float64[Flat],
    PP: Addr(Int32),
    TAU: Addr(Float64),
    SIGMA: Addr(Float64),
    DMIN: Addr(Float64),
    DMIN1: Addr(Float64),
    DMIN2: Addr(Float64),
    DN: Addr(Float64),
    DNM1: Addr(Float64),
    DNM2: Addr(Float64),
    IEEE: Addr(Bool),
    EPS: Addr(Float64)
) -> None: ...

@bind("DLASQ6")
@external
def dlasq6(
    I0: Addr(Int32),
    N0: Addr(Int32),
    Z: Float64[Flat],
    PP: Addr(Int32),
    DMIN: Addr(Float64),
    DMIN1: Addr(Float64),
    DMIN2: Addr(Float64),
    DN: Addr(Float64),
    DNM1: Addr(Float64),
    DNM2: Addr(Float64)
) -> None: ...

@bind("DLASR")
@external
def dlasr(
    SIDE: Addr(Const(String[1])),
    PIVOT: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    A: Float64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("DLASRT")
@external
def dlasrt(
    ID: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASSQ")
@external
def dlassq(
    n: Addr(Int32),
    x: Float64[Flat],
    incx: Addr(Int32),
    scale: Addr(Float64),
    sumsq: Addr(Float64)
) -> None: ...

@bind("DLASV2")
@external
def dlasv2(
    F: Addr(Float64),
    G: Addr(Float64),
    H: Addr(Float64),
    SSMIN: Addr(Float64),
    SSMAX: Addr(Float64),
    SNR: Addr(Float64),
    CSR: Addr(Float64),
    SNL: Addr(Float64),
    CSL: Addr(Float64)
) -> None: ...

@bind("DLASWLQ")
@external
def dlaswlq(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASWP")
@external
def dlaswp(
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    K1: Addr(Int32),
    K2: Addr(Int32),
    IPIV: Int32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("DLASY2")
@external
def dlasy2(
    LTRANL: Addr(Bool),
    LTRANR: Addr(Bool),
    ISGN: Addr(Int32),
    N1: Addr(Int32),
    N2: Addr(Int32),
    TL: Float64[LDTL, Flat],
    LDTL: Addr(Int32),
    TR: Float64[LDTR, Flat],
    LDTR: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    SCALE: Addr(Float64),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    XNORM: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASYF")
@external
def dlasyf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Float64[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASYF_AA")
@external
def dlasyf_aa(
    UPLO: Addr(Const(String[1])),
    J1: Addr(Int32),
    M: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    H: Float64[LDH, Flat],
    LDH: Addr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLASYF_RK")
@external
def dlasyf_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    W: Float64[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLASYF_ROOK")
@external
def dlasyf_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Float64[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAT2S")
@external
def dlat2s(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    SA: Float32[LDSA, Flat],
    LDSA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLATBS")
@external
def dlatbs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    X: Float64[Flat],
    SCALE: Addr(Float64),
    CNORM: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLATDF")
@external
def dlatdf(
    IJOB: Addr(Int32),
    N: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    RHS: Float64[Flat],
    RDSUM: Addr(Float64),
    RDSCAL: Addr(Float64),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("DLATPS")
@external
def dlatps(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    X: Float64[Flat],
    SCALE: Addr(Float64),
    CNORM: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLATRD")
@external
def dlatrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    TAU: Float64[Flat],
    W: Float64[LDW, Flat],
    LDW: Addr(Int32)
) -> None: ...

@bind("DLATRS")
@external
def dlatrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    X: Float64[Flat],
    SCALE: Addr(Float64),
    CNORM: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DLATRS3")
@external
def dlatrs3(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    SCALE: Float64[Flat],
    CNORM: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLATRZ")
@external
def dlatrz(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat]
) -> None: ...

@bind("DLATSQR")
@external
def dlatsqr(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAUU2")
@external
def dlauu2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DLAUUM")
@external
def dlauum(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DOPGTR")
@external
def dopgtr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    TAU: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DOPMTR")
@external
def dopmtr(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    AP: Float64[Flat],
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORBDB")
@external
def dorbdb(
    TRANS: Addr(Const(String[1])),
    SIGNS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Addr(Int32),
    X12: Float64[LDX12, Flat],
    LDX12: Addr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Addr(Int32),
    X22: Float64[LDX22, Flat],
    LDX22: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    TAUQ2: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORBDB1")
@external
def dorbdb1(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORBDB2")
@external
def dorbdb2(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORBDB3")
@external
def dorbdb3(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORBDB4")
@external
def dorbdb4(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    PHANTOM: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORBDB5")
@external
def dorbdb5(
    M1: Addr(Int32),
    M2: Addr(Int32),
    N: Addr(Int32),
    X1: Float64[Flat],
    INCX1: Addr(Int32),
    X2: Float64[Flat],
    INCX2: Addr(Int32),
    Q1: Float64[LDQ1, Flat],
    LDQ1: Addr(Int32),
    Q2: Float64[LDQ2, Flat],
    LDQ2: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORBDB6")
@external
def dorbdb6(
    M1: Addr(Int32),
    M2: Addr(Int32),
    N: Addr(Int32),
    X1: Float64[Flat],
    INCX1: Addr(Int32),
    X2: Float64[Flat],
    INCX2: Addr(Int32),
    Q1: Float64[LDQ1, Flat],
    LDQ1: Addr(Int32),
    Q2: Float64[LDQ2, Flat],
    LDQ2: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORCSD")
@external
def dorcsd(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    JOBV2T: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    SIGNS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Addr(Int32),
    X12: Float64[LDX12, Flat],
    LDX12: Addr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Addr(Int32),
    X22: Float64[LDX22, Flat],
    LDX22: Addr(Int32),
    THETA: Float64[Flat],
    U1: Float64[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Float64[LDV1T, Flat],
    LDV1T: Addr(Int32),
    V2T: Float64[LDV2T, Flat],
    LDV2T: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORCSD2BY1")
@external
def dorcsd2by1(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float64[Flat],
    U1: Float64[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Float64[LDV1T, Flat],
    LDV1T: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORG2L")
@external
def dorg2l(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORG2R")
@external
def dorg2r(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGBR")
@external
def dorgbr(
    VECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGHR")
@external
def dorghr(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGL2")
@external
def dorgl2(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGLQ")
@external
def dorglq(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGQL")
@external
def dorgql(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGQR")
@external
def dorgqr(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGR2")
@external
def dorgr2(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGRQ")
@external
def dorgrq(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGTR")
@external
def dorgtr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGTSQR")
@external
def dorgtsqr(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORGTSQR_ROW")
@external
def dorgtsqr_row(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORHR_COL")
@external
def dorhr_col(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    D: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORM22")
@external
def dorm22(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    N2: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORM2L")
@external
def dorm2l(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORM2R")
@external
def dorm2r(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORMBR")
@external
def dormbr(
    VECT: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORMHR")
@external
def dormhr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORML2")
@external
def dorml2(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORMLQ")
@external
def dormlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORMQL")
@external
def dormql(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORMQR")
@external
def dormqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORMR2")
@external
def dormr2(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORMR3")
@external
def dormr3(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DORMRQ")
@external
def dormrq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORMRZ")
@external
def dormrz(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DORMTR")
@external
def dormtr(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPBCON")
@external
def dpbcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPBEQU")
@external
def dpbequ(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPBRFS")
@external
def dpbrfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPBSTF")
@external
def dpbstf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPBSV")
@external
def dpbsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPBSVX")
@external
def dpbsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPBTF2")
@external
def dpbtf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPBTRF")
@external
def dpbtrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPBTRS")
@external
def dpbtrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPFTRF")
@external
def dpftrf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPFTRI")
@external
def dpftri(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPFTRS")
@external
def dpftrs(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOCON")
@external
def dpocon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOEQU")
@external
def dpoequ(
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOEQUB")
@external
def dpoequb(
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPORFS")
@external
def dporfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPORFSX")
@external
def dporfsx(
    UPLO: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOSV")
@external
def dposv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOSVX")
@external
def dposvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOSVXX")
@external
def dposvxx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    RPVGRW: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOTF2")
@external
def dpotf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOTRF")
@external
def dpotrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOTRF2")
@external
def dpotrf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOTRI")
@external
def dpotri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPOTRS")
@external
def dpotrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPPCON")
@external
def dppcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPPEQU")
@external
def dppequ(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPPRFS")
@external
def dpprfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPPSV")
@external
def dppsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPPSVX")
@external
def dppsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPPTRF")
@external
def dpptrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPPTRI")
@external
def dpptri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPPTRS")
@external
def dpptrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPSTF2")
@external
def dpstf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    PIV: Int32[N],
    RANK: Addr(Int32),
    TOL: Addr(Float64),
    WORK: Float64[2 * N],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPSTRF")
@external
def dpstrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    PIV: Int32[N],
    RANK: Addr(Int32),
    TOL: Addr(Float64),
    WORK: Float64[2 * N],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPTCON")
@external
def dptcon(
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPTEQR")
@external
def dpteqr(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPTRFS")
@external
def dptrfs(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    DF: Float64[Flat],
    EF: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPTSV")
@external
def dptsv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPTSVX")
@external
def dptsvx(
    FACT: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    DF: Float64[Flat],
    EF: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPTTRF")
@external
def dpttrf(
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DPTTRS")
@external
def dpttrs(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DPTTS2")
@external
def dptts2(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("DRSCL")
@external
def drscl(
    N: Addr(Int32),
    SA: Addr(Float64),
    SX: Float64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("DSB2ST_KERNELS")
@external
def dsb2st_kernels(
    UPLO: Addr(Const(String[1])),
    WANTZ: Addr(Bool),
    TTYPE: Addr(Int32),
    ST: Addr(Int32),
    ED: Addr(Int32),
    SWEEP: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    IB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    V: Float64[Flat],
    TAU: Float64[Flat],
    LDVT: Addr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DSBEV")
@external
def dsbev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSBEV_2STAGE")
@external
def dsbev_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSBEVD")
@external
def dsbevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSBEVD_2STAGE")
@external
def dsbevd_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSBEVX")
@external
def dsbevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSBEVX_2STAGE")
@external
def dsbevx_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSBGST")
@external
def dsbgst(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSBGV")
@external
def dsbgv(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSBGVD")
@external
def dsbgvd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSBGVX")
@external
def dsbgvx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSBTRD")
@external
def dsbtrd(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSFRK")
@external
def dsfrk(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    BETA: Addr(Float64),
    C: Float64[Flat]
) -> None: ...

@bind("DSGESV")
@external
def dsgesv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    WORK: Float64[N, Flat],
    SWORK: Float32[Flat],
    ITER: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPCON")
@external
def dspcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPEV")
@external
def dspev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPEVD")
@external
def dspevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPEVX")
@external
def dspevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPGST")
@external
def dspgst(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPGV")
@external
def dspgv(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPGVD")
@external
def dspgvd(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPGVX")
@external
def dspgvx(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPOSV")
@external
def dsposv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    WORK: Float64[N, Flat],
    SWORK: Float32[Flat],
    ITER: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPRFS")
@external
def dsprfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPSV")
@external
def dspsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPSVX")
@external
def dspsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPTRD")
@external
def dsptrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPTRF")
@external
def dsptrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPTRI")
@external
def dsptri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSPTRS")
@external
def dsptrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTEBZ")
@external
def dstebz(
    RANGE: Addr(Const(String[1])),
    ORDER: Addr(Const(String[1])),
    N: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    M: Addr(Int32),
    NSPLIT: Addr(Int32),
    W: Float64[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTEDC")
@external
def dstedc(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTEGR")
@external
def dstegr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTEIN")
@external
def dstein(
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    M: Addr(Int32),
    W: Float64[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTEMR")
@external
def dstemr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    NZC: Addr(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Addr(Bool),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTEQR")
@external
def dsteqr(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTERF")
@external
def dsterf(
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTEV")
@external
def dstev(
    JOBZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTEVD")
@external
def dstevd(
    JOBZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTEVR")
@external
def dstevr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSTEVX")
@external
def dstevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYCON")
@external
def dsycon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYCON_3")
@external
def dsycon_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYCON_ROOK")
@external
def dsycon_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYCONV")
@external
def dsyconv(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    E: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYCONVF")
@external
def dsyconvf(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYCONVF_ROOK")
@external
def dsyconvf_rook(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYEQUB")
@external
def dsyequb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYEV")
@external
def dsyev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYEV_2STAGE")
@external
def dsyev_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYEVD")
@external
def dsyevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYEVD_2STAGE")
@external
def dsyevd_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYEVR")
@external
def dsyevr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYEVR_2STAGE")
@external
def dsyevr_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYEVX")
@external
def dsyevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYEVX_2STAGE")
@external
def dsyevx_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYGS2")
@external
def dsygs2(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYGST")
@external
def dsygst(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYGV")
@external
def dsygv(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYGV_2STAGE")
@external
def dsygv_2stage(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYGVD")
@external
def dsygvd(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYGVX")
@external
def dsygvx(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYRFS")
@external
def dsyrfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYRFSX")
@external
def dsyrfsx(
    UPLO: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYSV")
@external
def dsysv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYSV_AA")
@external
def dsysv_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYSV_AA_2STAGE")
@external
def dsysv_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TB: Float64[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYSV_RK")
@external
def dsysv_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYSV_ROOK")
@external
def dsysv_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYSVX")
@external
def dsysvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYSVXX")
@external
def dsysvxx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    RPVGRW: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYSWAPR")
@external
def dsyswapr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    I1: Addr(Int32),
    I2: Addr(Int32)
) -> None: ...

@bind("DSYTD2")
@external
def dsytd2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTF2")
@external
def dsytf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTF2_RK")
@external
def dsytf2_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTF2_ROOK")
@external
def dsytf2_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRD")
@external
def dsytrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRD_2STAGE")
@external
def dsytrd_2stage(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    HOUS2: Float64[Flat],
    LHOUS2: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRD_SB2ST")
@external
def dsytrd_sb2st(
    STAGE1: Addr(Const(String[1])),
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    HOUS: Float64[Flat],
    LHOUS: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRD_SY2SB")
@external
def dsytrd_sy2sb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRF")
@external
def dsytrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRF_AA")
@external
def dsytrf_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRF_AA_2STAGE")
@external
def dsytrf_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TB: Float64[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRF_RK")
@external
def dsytrf_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRF_ROOK")
@external
def dsytrf_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRI")
@external
def dsytri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRI2")
@external
def dsytri2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRI2X")
@external
def dsytri2x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRI_3")
@external
def dsytri_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRI_3X")
@external
def dsytri_3x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRI_ROOK")
@external
def dsytri_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRS")
@external
def dsytrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRS2")
@external
def dsytrs2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRS_3")
@external
def dsytrs_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRS_AA")
@external
def dsytrs_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRS_AA_2STAGE")
@external
def dsytrs_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TB: Float64[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DSYTRS_ROOK")
@external
def dsytrs_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTBCON")
@external
def dtbcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTBRFS")
@external
def dtbrfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTBTRS")
@external
def dtbtrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTFSM")
@external
def dtfsm(
    TRANSR: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    B: Annotated[Float64[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Addr(Int32)
) -> None: ...

@bind("DTFTRI")
@external
def dtftri(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTFTTP")
@external
def dtfttp(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    AP: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTFTTR")
@external
def dtfttr(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    A: Annotated[Float64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTGEVC")
@external
def dtgevc(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    S: Float64[LDS, Flat],
    LDS: Addr(Int32),
    P: Float64[LDP, Flat],
    LDP: Addr(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTGEX2")
@external
def dtgex2(
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    J1: Addr(Int32),
    N1: Addr(Int32),
    N2: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTGEXC")
@external
def dtgexc(
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    IFST: Addr(Int32),
    ILST: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTGSEN")
@external
def dtgsen(
    IJOB: Addr(Int32),
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Addr(Int32),
    M: Addr(Int32),
    PL: Addr(Float64),
    PR: Addr(Float64),
    DIF: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTGSJA")
@external
def dtgsja(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    TOLA: Addr(Float64),
    TOLB: Addr(Float64),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Float64[Flat],
    NCYCLE: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTGSNA")
@external
def dtgsna(
    JOB: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    S: Float64[Flat],
    DIF: Float64[Flat],
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTGSY2")
@external
def dtgsy2(
    TRANS: Addr(Const(String[1])),
    IJOB: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    D: Float64[LDD, Flat],
    LDD: Addr(Int32),
    E: Float64[LDE, Flat],
    LDE: Addr(Int32),
    F: Float64[LDF, Flat],
    LDF: Addr(Int32),
    SCALE: Addr(Float64),
    RDSUM: Addr(Float64),
    RDSCAL: Addr(Float64),
    IWORK: Int32[Flat],
    PQ: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTGSYL")
@external
def dtgsyl(
    TRANS: Addr(Const(String[1])),
    IJOB: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    D: Float64[LDD, Flat],
    LDD: Addr(Int32),
    E: Float64[LDE, Flat],
    LDE: Addr(Int32),
    F: Float64[LDF, Flat],
    LDF: Addr(Int32),
    SCALE: Addr(Float64),
    DIF: Addr(Float64),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPCON")
@external
def dtpcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPLQT")
@external
def dtplqt(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    MB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPLQT2")
@external
def dtplqt2(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPMLQT")
@external
def dtpmlqt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    MB: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPMQRT")
@external
def dtpmqrt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    NB: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPQRT")
@external
def dtpqrt(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    NB: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPQRT2")
@external
def dtpqrt2(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPRFB")
@external
def dtprfb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    V: Float64[LDV, Flat],
    LDV: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("DTPRFS")
@external
def dtprfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPTRI")
@external
def dtptri(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPTRS")
@external
def dtptrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPTTF")
@external
def dtpttf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Annotated[Float64[Flat], SourceDims("0:*")],
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTPTTR")
@external
def dtpttr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRCON")
@external
def dtrcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    RCOND: Addr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTREVC")
@external
def dtrevc(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTREVC3")
@external
def dtrevc3(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTREXC")
@external
def dtrexc(
    COMPQ: Addr(Const(String[1])),
    N: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    IFST: Addr(Int32),
    ILST: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRRFS")
@external
def dtrrfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    X: Float64[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRSEN")
@external
def dtrsen(
    JOB: Addr(Const(String[1])),
    COMPQ: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Addr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    M: Addr(Int32),
    S: Addr(Float64),
    SEP: Addr(Float64),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRSNA")
@external
def dtrsna(
    JOB: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Float64[LDT, Flat],
    LDT: Addr(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Addr(Int32),
    S: Float64[Flat],
    SEP: Float64[Flat],
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRSYL")
@external
def dtrsyl(
    TRANA: Addr(Const(String[1])),
    TRANB: Addr(Const(String[1])),
    ISGN: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    SCALE: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRSYL3")
@external
def dtrsyl3(
    TRANA: Addr(Const(String[1])),
    TRANB: Addr(Const(String[1])),
    ISGN: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32),
    SCALE: Addr(Float64),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    SWORK: Float64[LDSWORK, Flat],
    LDSWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRTI2")
@external
def dtrti2(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRTRI")
@external
def dtrtri(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRTRS")
@external
def dtrtrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRTTF")
@external
def dtrttf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Float64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Addr(Int32),
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTRTTP")
@external
def dtrttp(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    AP: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("DTZRZF")
@external
def dtzrzf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("DZSUM1")
@external
def dzsum1(
    N: Addr(Int32),
    CX: Complex128[Flat],
    INCX: Addr(Int32)
) -> Float64: ...

@bind("ICMAX1")
@external
def icmax1(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32)
) -> Int32: ...

@bind("IEEECK")
@external
def ieeeck(
    ISPEC: Addr(Int32),
    ZERO: Addr(Float32),
    ONE: Addr(Float32)
) -> Int32: ...

@bind("ILACLC")
@external
def ilaclc(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32)
) -> Int32: ...

@bind("ILACLR")
@external
def ilaclr(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32)
) -> Int32: ...

@bind("ILADIAG")
@external
def iladiag(
    DIAG: Addr(Const(String[1]))
) -> Int32: ...

@bind("ILADLC")
@external
def iladlc(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32)
) -> Int32: ...

@bind("ILADLR")
@external
def iladlr(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32)
) -> Int32: ...

@bind("ILAENV")
@external
def ilaenv(
    ISPEC: Addr(Int32),
    NAME: Addr(Const(String)),
    OPTS: Addr(Const(String)),
    N1: Addr(Int32),
    N2: Addr(Int32),
    N3: Addr(Int32),
    N4: Addr(Int32)
) -> Int32: ...

@bind("ILAENV2STAGE")
@external
def ilaenv2stage(
    ISPEC: Addr(Int32),
    NAME: Addr(Const(String)),
    OPTS: Addr(Const(String)),
    N1: Addr(Int32),
    N2: Addr(Int32),
    N3: Addr(Int32),
    N4: Addr(Int32)
) -> Int32: ...

@bind("ILAPREC")
@external
def ilaprec(
    PREC: Addr(Const(String[1]))
) -> Int32: ...

@bind("ILASLC")
@external
def ilaslc(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32)
) -> Int32: ...

@bind("ILASLR")
@external
def ilaslr(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32)
) -> Int32: ...

@bind("ILATRANS")
@external
def ilatrans(
    TRANS: Addr(Const(String[1]))
) -> Int32: ...

@bind("ILAUPLO")
@external
def ilauplo(
    UPLO: Addr(Const(String[1]))
) -> Int32: ...

@bind("ILAZLC")
@external
def ilazlc(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32)
) -> Int32: ...

@bind("ILAZLR")
@external
def ilazlr(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32)
) -> Int32: ...

@bind("IPARAM2STAGE")
@external
def iparam2stage(
    ISPEC: Addr(Int32),
    NAME: Addr(Const(String)),
    OPTS: Addr(Const(String)),
    NI: Addr(Int32),
    NBI: Addr(Int32),
    IBI: Addr(Int32),
    NXI: Addr(Int32)
) -> Int32: ...

@bind("IPARMQ")
@external
def iparmq(
    ISPEC: Addr(Int32),
    NAME: String[1][Flat],
    OPTS: String[1][Flat],
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LWORK: Addr(Int32)
) -> Int32: ...

@bind("IZMAX1")
@external
def izmax1(
    N: Addr(Int32),
    ZX: Complex128[Flat],
    INCX: Addr(Int32)
) -> Int32: ...

@bind("LSAMEN")
@external
def lsamen(
    N: Addr(Int32),
    CA: Addr(Const(String)),
    CB: Addr(Const(String))
) -> Bool: ...

@bind("SBBCSD")
@external
def sbbcsd(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    JOBV2T: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    U1: Float32[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Float32[LDV1T, Flat],
    LDV1T: Addr(Int32),
    V2T: Float32[LDV2T, Flat],
    LDV2T: Addr(Int32),
    B11D: Float32[Flat],
    B11E: Float32[Flat],
    B12D: Float32[Flat],
    B12E: Float32[Flat],
    B21D: Float32[Flat],
    B21E: Float32[Flat],
    B22D: Float32[Flat],
    B22E: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SBDSDC")
@external
def sbdsdc(
    UPLO: Addr(Const(String[1])),
    COMPQ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Addr(Int32),
    Q: Float32[Flat],
    IQ: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SBDSQR")
@external
def sbdsqr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NCVT: Addr(Int32),
    NRU: Addr(Int32),
    NCC: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VT: Float32[LDVT, Flat],
    LDVT: Addr(Int32),
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SBDSVDX")
@external
def sbdsvdx(
    UPLO: Addr(Const(String[1])),
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    NS: Addr(Int32),
    S: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SCSUM1")
@external
def scsum1(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32)
) -> Float32: ...

@bind("SDISNA")
@external
def sdisna(
    JOB: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    D: Float32[Flat],
    SEP: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBBRD")
@external
def sgbbrd(
    VECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NCC: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    PT: Float32[LDPT, Flat],
    LDPT: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBCON")
@external
def sgbcon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBEQU")
@external
def sgbequ(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBEQUB")
@external
def sgbequb(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBRFS")
@external
def sgbrfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBRFSX")
@external
def sgbrfsx(
    TRANS: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBSV")
@external
def sgbsv(
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBSVX")
@external
def sgbsvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBSVXX")
@external
def sgbsvxx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    RPVGRW: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBTF2")
@external
def sgbtf2(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBTRF")
@external
def sgbtrf(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGBTRS")
@external
def sgbtrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEBAK")
@external
def sgebak(
    JOB: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float32[Flat],
    M: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEBAL")
@external
def sgebal(
    JOB: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEBD2")
@external
def sgebd2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Float32[Flat],
    TAUP: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEBRD")
@external
def sgebrd(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Float32[Flat],
    TAUP: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGECON")
@external
def sgecon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Addr(Arg(11)), Addr(Arg(12)), Return('K', 0), Arg(13), Arg(14), Arg(15), Addr(Arg(16)), Arg(17), Arg(18), Addr(Arg(19)), Arg(20), Addr(Arg(21)), Arg(22), Addr(Arg(23)), Arg(24), Addr(Arg(25)), Arg(26), Addr(Arg(27)), Return('INFO', 10)])
def sgedmd(
    JOBS: Addr(Const(String[1])),
    JOBZ: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBF: Addr(Const(String[1])),
    WHTSVD: Const(Int32),
    M: Const(Int32),
    N: Const(Int32),
    X: Float32[LDX, Flat],
    LDX: Const(Int32),
    Y: Float32[LDY, Flat],
    LDY: Const(Int32),
    NRNK: Const(Int32),
    TOL: Const(Float32),
    REIG: Float32[Flat],
    IMEIG: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Const(Int32),
    RES: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Const(Int32),
    W: Float32[LDW, Flat],
    LDW: Const(Int32),
    S: Float32[LDS, Flat],
    LDS: Const(Int32),
    WORK: Float32[Flat],
    LWORK: Const(Int32),
    IWORK: Int32[Flat],
    LIWORK: Const(Int32)
) -> tuple[Int32, Returns["REIG", Float32[Flat]], Returns["IMEIG", Float32[Flat]], Returns["Z", Float32[LDZ, Flat]], Returns["RES", Float32[Flat]], Returns["B", Float32[LDB, Flat]], Returns["W", Float32[LDW, Flat]], Returns["S", Float32[LDS, Flat]], Returns["WORK", Float32[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("SGEDMDQ")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Arg(11), Addr(Arg(12)), Arg(13), Addr(Arg(14)), Addr(Arg(15)), Addr(Arg(16)), Return('K', 2), Arg(17), Arg(18), Arg(19), Addr(Arg(20)), Arg(21), Arg(22), Addr(Arg(23)), Arg(24), Addr(Arg(25)), Arg(26), Addr(Arg(27)), Arg(28), Addr(Arg(29)), Arg(30), Addr(Arg(31)), Return('INFO', 12)])
def sgedmdq(
    JOBS: Addr(Const(String[1])),
    JOBZ: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    JOBT: Addr(Const(String[1])),
    JOBF: Addr(Const(String[1])),
    WHTSVD: Const(Int32),
    M: Const(Int32),
    N: Const(Int32),
    F: Float32[LDF, Flat],
    LDF: Const(Int32),
    X: Float32[LDX, Flat],
    LDX: Const(Int32),
    Y: Float32[LDY, Flat],
    LDY: Const(Int32),
    NRNK: Const(Int32),
    TOL: Const(Float32),
    REIG: Float32[Flat],
    IMEIG: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Const(Int32),
    RES: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Const(Int32),
    V: Float32[LDV, Flat],
    LDV: Const(Int32),
    S: Float32[LDS, Flat],
    LDS: Const(Int32),
    WORK: Float32[Flat],
    LWORK: Const(Int32),
    IWORK: Int32[Flat],
    LIWORK: Const(Int32)
) -> tuple[Returns["X", Float32[LDX, Flat]], Returns["Y", Float32[LDY, Flat]], Int32, Returns["REIG", Float32[Flat]], Returns["IMEIG", Float32[Flat]], Returns["Z", Float32[LDZ, Flat]], Returns["RES", Float32[Flat]], Returns["B", Float32[LDB, Flat]], Returns["V", Float32[LDV, Flat]], Returns["S", Float32[LDS, Flat]], Returns["WORK", Float32[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("SGEEQU")
@external
def sgeequ(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEEQUB")
@external
def sgeequb(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEES")
@external
def sgees(
    JOBVS: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELECT: Addr(Bool),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    SDIM: Addr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VS: Float32[LDVS, Flat],
    LDVS: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEESX")
@external
def sgeesx(
    JOBVS: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELECT: Addr(Bool),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    SDIM: Addr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VS: Float32[LDVS, Flat],
    LDVS: Addr(Int32),
    RCONDE: Addr(Float32),
    RCONDV: Addr(Float32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEEV")
@external
def sgeev(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEEVX")
@external
def sgeevx(
    BALANC: Addr(Const(String[1])),
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float32[Flat],
    ABNRM: Addr(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEHD2")
@external
def sgehd2(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEHRD")
@external
def sgehrd(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEJSV")
@external
def sgejsv(
    JOBA: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBT: Addr(Const(String[1])),
    JOBP: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    SVA: Float32[N],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    WORK: Float32[LWORK],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGELQ")
@external
def sgelq(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[Flat],
    TSIZE: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGELQ2")
@external
def sgelq2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGELQF")
@external
def sgelqf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGELQT")
@external
def sgelqt(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGELQT3")
@external
def sgelqt3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGELS")
@external
def sgels(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGELSD")
@external
def sgelsd(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    S: Float32[Flat],
    RCOND: Addr(Float32),
    RANK: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGELSS")
@external
def sgelss(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    S: Float32[Flat],
    RCOND: Addr(Float32),
    RANK: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGELST")
@external
def sgelst(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGELSY")
@external
def sgelsy(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    JPVT: Int32[Flat],
    RCOND: Addr(Float32),
    RANK: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEMLQ")
@external
def sgemlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[Flat],
    TSIZE: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEMLQT")
@external
def sgemlqt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEMQR")
@external
def sgemqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[Flat],
    TSIZE: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEMQRT")
@external
def sgemqrt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    NB: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQL2")
@external
def sgeql2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQLF")
@external
def sgeqlf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQP3")
@external
def sgeqp3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQP3RK")
@external
def sgeqp3rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    KMAX: Addr(Int32),
    ABSTOL: Addr(Float32),
    RELTOL: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    K: Addr(Int32),
    MAXC2NRMK: Addr(Float32),
    RELMAXC2NRMK: Addr(Float32),
    JPIV: Int32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQR")
@external
def sgeqr(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[Flat],
    TSIZE: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQR2")
@external
def sgeqr2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQR2P")
@external
def sgeqr2p(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQRF")
@external
def sgeqrf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQRFP")
@external
def sgeqrfp(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQRT")
@external
def sgeqrt(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQRT2")
@external
def sgeqrt2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGEQRT3")
@external
def sgeqrt3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGERFS")
@external
def sgerfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGERFSX")
@external
def sgerfsx(
    TRANS: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGERQ2")
@external
def sgerq2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGERQF")
@external
def sgerqf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGESC2")
@external
def sgesc2(
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    RHS: Float32[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Addr(Float32)
) -> None: ...

@bind("SGESDD")
@external
def sgesdd(
    JOBZ: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGESV")
@external
def sgesv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGESVD")
@external
def sgesvd(
    JOBU: Addr(Const(String[1])),
    JOBVT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGESVDQ")
@external
def sgesvdq(
    JOBA: Addr(Const(String[1])),
    JOBP: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    NUMRANK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGESVDX")
@external
def sgesvdx(
    JOBU: Addr(Const(String[1])),
    JOBVT: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    NS: Addr(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGESVJ")
@external
def sgesvj(
    JOBA: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    SVA: Float32[N],
    MV: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    WORK: Float32[LWORK],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGESVX")
@external
def sgesvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGESVXX")
@external
def sgesvxx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    RPVGRW: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGETC2")
@external
def sgetc2(
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGETF2")
@external
def sgetf2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGETRF")
@external
def sgetrf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGETRF2")
@external
def sgetrf2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGETRI")
@external
def sgetri(
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGETRS")
@external
def sgetrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGETSLS")
@external
def sgetsls(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGETSQRHRT")
@external
def sgetsqrhrt(
    M: Addr(Int32),
    N: Addr(Int32),
    MB1: Addr(Int32),
    NB1: Addr(Int32),
    NB2: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGBAK")
@external
def sggbak(
    JOB: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    M: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGBAL")
@external
def sggbal(
    JOB: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGES")
@external
def sgges(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VSL: Float32[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Float32[LDVSR, Flat],
    LDVSR: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGES3")
@external
def sgges3(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VSL: Float32[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Float32[LDVSR, Flat],
    LDVSR: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGESX")
@external
def sggesx(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VSL: Float32[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Float32[LDVSR, Flat],
    LDVSR: Addr(Int32),
    RCONDE: Float32[2],
    RCONDV: Float32[2],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGEV")
@external
def sggev(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGEV3")
@external
def sggev3(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGEVX")
@external
def sggevx(
    BALANC: Addr(Const(String[1])),
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    ABNRM: Addr(Float32),
    BBNRM: Addr(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGGLM")
@external
def sggglm(
    N: Addr(Int32),
    M: Addr(Int32),
    P: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    D: Float32[Flat],
    X: Float32[Flat],
    Y: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGHD3")
@external
def sgghd3(
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGHRD")
@external
def sgghrd(
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGLSE")
@external
def sgglse(
    M: Addr(Int32),
    N: Addr(Int32),
    P: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    C: Float32[Flat],
    D: Float32[Flat],
    X: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGQRF")
@external
def sggqrf(
    N: Addr(Int32),
    M: Addr(Int32),
    P: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAUA: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    TAUB: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGRQF")
@external
def sggrqf(
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAUA: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    TAUB: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGSVD3")
@external
def sggsvd3(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    P: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGGSVP3")
@external
def sggsvp3(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    TOLA: Addr(Float32),
    TOLB: Addr(Float32),
    K: Addr(Int32),
    L: Addr(Int32),
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    IWORK: Int32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGSVJ0")
@external
def sgsvj0(
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[N],
    SVA: Float32[N],
    MV: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    EPS: Addr(Float32),
    SFMIN: Addr(Float32),
    TOL: Addr(Float32),
    NSWEEP: Addr(Int32),
    WORK: Float32[LWORK],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGSVJ1")
@external
def sgsvj1(
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[N],
    SVA: Float32[N],
    MV: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    EPS: Addr(Float32),
    SFMIN: Addr(Float32),
    TOL: Addr(Float32),
    NSWEEP: Addr(Int32),
    WORK: Float32[LWORK],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGTCON")
@external
def sgtcon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGTRFS")
@external
def sgtrfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DLF: Float32[Flat],
    DF: Float32[Flat],
    DUF: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGTSV")
@external
def sgtsv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGTSVX")
@external
def sgtsvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DLF: Float32[Flat],
    DF: Float32[Flat],
    DUF: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGTTRF")
@external
def sgttrf(
    N: Addr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SGTTRS")
@external
def sgttrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SGTTS2")
@external
def sgtts2(
    ITRANS: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("SHGEQZ")
@external
def shgeqz(
    JOB: Addr(Const(String[1])),
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SHSEIN")
@external
def shsein(
    SIDE: Addr(Const(String[1])),
    EIGSRC: Addr(Const(String[1])),
    INITV: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float32[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SHSEQR")
@external
def shseqr(
    JOB: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SISNAN")
@external
@native_call([Addr(Arg(0))])
def sisnan(
    SIN: Const(Float32)
) -> Bool: ...

@bind("SLA_GBAMV")
@external
def sla_gbamv(
    TRANS: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    ALPHA: Addr(Float32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float32),
    Y: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("SLA_GBRCOND")
@external
def sla_gbrcond(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    CMODE: Addr(Int32),
    C: Float32[Flat],
    INFO: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_GBRFSX_EXTENDED")
@external
def sla_gbrfsx_extended(
    PREC_TYPE: Addr(Int32),
    TRANS_TYPE: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    Y: Float32[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Addr(Float32),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float32),
    DZ_UB: Addr(Float32),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLA_GBRPVGRW")
@external
def sla_gbrpvgrw(
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NCOLS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Addr(Int32)
) -> Float32: ...

@bind("SLA_GEAMV")
@external
def sla_geamv(
    TRANS: Addr(Int32),
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

@bind("SLA_GERCOND")
@external
def sla_gercond(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    CMODE: Addr(Int32),
    C: Float32[Flat],
    INFO: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_GERFSX_EXTENDED")
@external
def sla_gerfsx_extended(
    PREC_TYPE: Addr(Int32),
    TRANS_TYPE: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    Y: Float32[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Addr(Int32),
    ERRS_N: Float32[NRHS, Flat],
    ERRS_C: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Addr(Float32),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float32),
    DZ_UB: Addr(Float32),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLA_GERPVGRW")
@external
def sla_gerpvgrw(
    N: Addr(Int32),
    NCOLS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32)
) -> Float32: ...

@bind("SLA_LIN_BERR")
@external
def sla_lin_berr(
    N: Addr(Int32),
    NZ: Addr(Int32),
    NRHS: Addr(Int32),
    RES: Annotated[Float32[N, NRHS], ORDER_F],
    AYB: Annotated[Float32[N, NRHS], ORDER_F],
    BERR: Float32[NRHS]
) -> None: ...

@bind("SLA_PORCOND")
@external
def sla_porcond(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    CMODE: Addr(Int32),
    C: Float32[Flat],
    INFO: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_PORFSX_EXTENDED")
@external
def sla_porfsx_extended(
    PREC_TYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    COLEQU: Addr(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    Y: Float32[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Addr(Float32),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float32),
    DZ_UB: Addr(Float32),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLA_PORPVGRW")
@external
def sla_porpvgrw(
    UPLO: Addr(Const(String[1])),
    NCOLS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLA_SYAMV")
@external
def sla_syamv(
    UPLO: Addr(Int32),
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

@bind("SLA_SYRCOND")
@external
def sla_syrcond(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    CMODE: Addr(Int32),
    C: Float32[Flat],
    INFO: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_SYRFSX_EXTENDED")
@external
def sla_syrfsx_extended(
    PREC_TYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    Y: Float32[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Addr(Float32),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float32),
    DZ_UB: Addr(Float32),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLA_SYRPVGRW")
@external
def sla_syrpvgrw(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    INFO: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLA_WWADDW")
@external
def sla_wwaddw(
    N: Addr(Int32),
    X: Float32[Flat],
    Y: Float32[Flat],
    W: Float32[Flat]
) -> None: ...

@bind("SLABAD")
@external
def slabad(
    SMALL: Addr(Float32),
    LARGE: Addr(Float32)
) -> None: ...

@bind("SLABRD")
@external
def slabrd(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Float32[Flat],
    TAUP: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    Y: Float32[LDY, Flat],
    LDY: Addr(Int32)
) -> None: ...

@bind("SLACN2")
@external
def slacn2(
    N: Addr(Int32),
    V: Float32[Flat],
    X: Float32[Flat],
    ISGN: Int32[Flat],
    EST: Addr(Float32),
    KASE: Addr(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("SLACON")
@external
def slacon(
    N: Addr(Int32),
    V: Float32[Flat],
    X: Float32[Flat],
    ISGN: Int32[Flat],
    EST: Addr(Float32),
    KASE: Addr(Int32)
) -> None: ...

@bind("SLACPY")
@external
def slacpy(
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("SLADIV")
@external
def sladiv(
    A: Addr(Float32),
    B: Addr(Float32),
    C: Addr(Float32),
    D: Addr(Float32),
    P: Addr(Float32),
    Q: Addr(Float32)
) -> None: ...

@bind("SLADIV1")
@external
def sladiv1(
    A: Addr(Float32),
    B: Addr(Float32),
    C: Addr(Float32),
    D: Addr(Float32),
    P: Addr(Float32),
    Q: Addr(Float32)
) -> None: ...

@bind("SLADIV2")
@external
def sladiv2(
    A: Addr(Float32),
    B: Addr(Float32),
    C: Addr(Float32),
    D: Addr(Float32),
    R: Addr(Float32),
    T: Addr(Float32)
) -> Float32: ...

@bind("SLAE2")
@external
def slae2(
    A: Addr(Float32),
    B: Addr(Float32),
    C: Addr(Float32),
    RT1: Addr(Float32),
    RT2: Addr(Float32)
) -> None: ...

@bind("SLAEBZ")
@external
def slaebz(
    IJOB: Addr(Int32),
    NITMAX: Addr(Int32),
    N: Addr(Int32),
    MMAX: Addr(Int32),
    MINP: Addr(Int32),
    NBMIN: Addr(Int32),
    ABSTOL: Addr(Float32),
    RELTOL: Addr(Float32),
    PIVMIN: Addr(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    NVAL: Int32[Flat],
    AB: Float32[MMAX, Flat],
    C: Float32[Flat],
    MOUT: Addr(Int32),
    NAB: Int32[MMAX, Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAED0")
@external
def slaed0(
    ICOMPQ: Addr(Int32),
    QSIZ: Addr(Int32),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    QSTORE: Float32[LDQS, Flat],
    LDQS: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAED1")
@external
def slaed1(
    N: Addr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    INDXQ: Int32[Flat],
    RHO: Addr(Float32),
    CUTPNT: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAED2")
@external
def slaed2(
    K: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    INDXQ: Int32[Flat],
    RHO: Addr(Float32),
    Z: Float32[Flat],
    DLAMBDA: Float32[Flat],
    W: Float32[Flat],
    Q2: Float32[Flat],
    INDX: Int32[Flat],
    INDXC: Int32[Flat],
    INDXP: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAED3")
@external
def slaed3(
    K: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    RHO: Addr(Float32),
    DLAMBDA: Float32[Flat],
    Q2: Float32[Flat],
    INDX: Int32[Flat],
    CTOT: Int32[Flat],
    W: Float32[Flat],
    S: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAED4")
@external
def slaed4(
    N: Addr(Int32),
    I: Addr(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    DELTA: Float32[Flat],
    RHO: Addr(Float32),
    DLAM: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAED5")
@external
def slaed5(
    I: Addr(Int32),
    D: Float32[2],
    Z: Float32[2],
    DELTA: Float32[2],
    RHO: Addr(Float32),
    DLAM: Addr(Float32)
) -> None: ...

@bind("SLAED6")
@external
def slaed6(
    KNITER: Addr(Int32),
    ORGATI: Addr(Bool),
    RHO: Addr(Float32),
    D: Float32[3],
    Z: Float32[3],
    FINIT: Addr(Float32),
    TAU: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAED7")
@external
def slaed7(
    ICOMPQ: Addr(Int32),
    N: Addr(Int32),
    QSIZ: Addr(Int32),
    TLVLS: Addr(Int32),
    CURLVL: Addr(Int32),
    CURPBM: Addr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    INDXQ: Int32[Flat],
    RHO: Addr(Float32),
    CUTPNT: Addr(Int32),
    QSTORE: Float32[Flat],
    QPTR: Int32[Flat],
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAED8")
@external
def slaed8(
    ICOMPQ: Addr(Int32),
    K: Addr(Int32),
    N: Addr(Int32),
    QSIZ: Addr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    INDXQ: Int32[Flat],
    RHO: Addr(Float32),
    CUTPNT: Addr(Int32),
    Z: Float32[Flat],
    DLAMBDA: Float32[Flat],
    Q2: Float32[LDQ2, Flat],
    LDQ2: Addr(Int32),
    W: Float32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAED9")
@external
def slaed9(
    K: Addr(Int32),
    KSTART: Addr(Int32),
    KSTOP: Addr(Int32),
    N: Addr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    RHO: Addr(Float32),
    DLAMBDA: Float32[Flat],
    W: Float32[Flat],
    S: Float32[LDS, Flat],
    LDS: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAEDA")
@external
def slaeda(
    N: Addr(Int32),
    TLVLS: Addr(Int32),
    CURLVL: Addr(Int32),
    CURPBM: Addr(Int32),
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    Q: Float32[Flat],
    QPTR: Int32[Flat],
    Z: Float32[Flat],
    ZTEMP: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAEIN")
@external
def slaein(
    RIGHTV: Addr(Bool),
    NOINIT: Addr(Bool),
    N: Addr(Int32),
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    WR: Addr(Float32),
    WI: Addr(Float32),
    VR: Float32[Flat],
    VI: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    EPS3: Addr(Float32),
    SMLNUM: Addr(Float32),
    BIGNUM: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAEV2")
@external
def slaev2(
    A: Addr(Float32),
    B: Addr(Float32),
    C: Addr(Float32),
    RT1: Addr(Float32),
    RT2: Addr(Float32),
    CS1: Addr(Float32),
    SN1: Addr(Float32)
) -> None: ...

@bind("SLAEXC")
@external
def slaexc(
    WANTQ: Addr(Bool),
    N: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    J1: Addr(Int32),
    N1: Addr(Int32),
    N2: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAG2")
@external
def slag2(
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    SAFMIN: Addr(Float32),
    SCALE1: Addr(Float32),
    SCALE2: Addr(Float32),
    WR1: Addr(Float32),
    WR2: Addr(Float32),
    WI: Addr(Float32)
) -> None: ...

@bind("SLAG2D")
@external
def slag2d(
    M: Addr(Int32),
    N: Addr(Int32),
    SA: Float32[LDSA, Flat],
    LDSA: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAGS2")
@external
def slags2(
    UPPER: Addr(Bool),
    A1: Addr(Float32),
    A2: Addr(Float32),
    A3: Addr(Float32),
    B1: Addr(Float32),
    B2: Addr(Float32),
    B3: Addr(Float32),
    CSU: Addr(Float32),
    SNU: Addr(Float32),
    CSV: Addr(Float32),
    SNV: Addr(Float32),
    CSQ: Addr(Float32),
    SNQ: Addr(Float32)
) -> None: ...

@bind("SLAGTF")
@external
def slagtf(
    N: Addr(Int32),
    A: Float32[Flat],
    LAMBDA: Addr(Float32),
    B: Float32[Flat],
    C: Float32[Flat],
    TOL: Addr(Float32),
    D: Float32[Flat],
    IN: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAGTM")
@external
def slagtm(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    ALPHA: Addr(Float32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    BETA: Addr(Float32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("SLAGTS")
@external
def slagts(
    JOB: Addr(Int32),
    N: Addr(Int32),
    A: Float32[Flat],
    B: Float32[Flat],
    C: Float32[Flat],
    D: Float32[Flat],
    IN: Int32[Flat],
    Y: Float32[Flat],
    TOL: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAGV2")
@external
def slagv2(
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    ALPHAR: Float32[2],
    ALPHAI: Float32[2],
    BETA: Float32[2],
    CSL: Addr(Float32),
    SNL: Addr(Float32),
    CSR: Addr(Float32),
    SNR: Addr(Float32)
) -> None: ...

@bind("SLAHQR")
@external
def slahqr(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAHR2")
@external
def slahr2(
    N: Addr(Int32),
    K: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[NB],
    T: Annotated[Float32[LDT, NB], ORDER_F],
    LDT: Addr(Int32),
    Y: Annotated[Float32[LDY, NB], ORDER_F],
    LDY: Addr(Int32)
) -> None: ...

@bind("SLAIC1")
@external
def slaic1(
    JOB: Addr(Int32),
    J: Addr(Int32),
    X: Float32[J],
    SEST: Addr(Float32),
    W: Float32[J],
    GAMMA: Addr(Float32),
    SESTPR: Addr(Float32),
    S: Addr(Float32),
    C: Addr(Float32)
) -> None: ...

@bind("SLAISNAN")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1))])
def slaisnan(
    SIN1: Const(Float32),
    SIN2: Const(Float32)
) -> Bool: ...

@bind("SLALN2")
@external
def slaln2(
    LTRANS: Addr(Bool),
    NA: Addr(Int32),
    NW: Addr(Int32),
    SMIN: Addr(Float32),
    CA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D1: Addr(Float32),
    D2: Addr(Float32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WR: Addr(Float32),
    WI: Addr(Float32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    SCALE: Addr(Float32),
    XNORM: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLALS0")
@external
def slals0(
    ICOMPQ: Addr(Int32),
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    NRHS: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    BX: Float32[LDBX, Flat],
    LDBX: Addr(Int32),
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Addr(Int32),
    POLES: Float32[LDGNUM, Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[LDGNUM, Flat],
    Z: Float32[Flat],
    K: Addr(Int32),
    C: Addr(Float32),
    S: Addr(Float32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLALSA")
@external
def slalsa(
    ICOMPQ: Addr(Int32),
    SMLSIZ: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    BX: Float32[LDBX, Flat],
    LDBX: Addr(Int32),
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float32[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float32[LDU, Flat],
    DIFR: Float32[LDU, Flat],
    Z: Float32[LDU, Flat],
    POLES: Float32[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float32[LDU, Flat],
    C: Float32[Flat],
    S: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLALSD")
@external
def slalsd(
    UPLO: Addr(Const(String[1])),
    SMLSIZ: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    RCOND: Addr(Float32),
    RANK: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAMRG")
@external
def slamrg(
    N1: Addr(Int32),
    N2: Addr(Int32),
    A: Float32[Flat],
    STRD1: Addr(Int32),
    STRD2: Addr(Int32),
    INDEX: Int32[Flat]
) -> None: ...

@bind("SLAMSWLQ")
@external
def slamswlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAMTSQR")
@external
def slamtsqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLANEG")
@external
def slaneg(
    N: Addr(Int32),
    D: Float32[Flat],
    LLD: Float32[Flat],
    SIGMA: Addr(Float32),
    PIVMIN: Addr(Float32),
    R: Addr(Int32)
) -> Int32: ...

@bind("SLANGB")
@external
def slangb(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANGE")
@external
def slange(
    NORM: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANGT")
@external
def slangt(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat]
) -> Float32: ...

@bind("SLANHS")
@external
def slanhs(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANSB")
@external
def slansb(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANSF")
@external
def slansf(
    NORM: Addr(Const(String[1])),
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    WORK: Annotated[Float32[Flat], SourceDims("0:*")]
) -> Float32: ...

@bind("SLANSP")
@external
def slansp(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANST")
@external
def slanst(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat]
) -> Float32: ...

@bind("SLANSY")
@external
def slansy(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANTB")
@external
def slantb(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANTP")
@external
def slantp(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANTR")
@external
def slantr(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANV2")
@external
def slanv2(
    A: Addr(Float32),
    B: Addr(Float32),
    C: Addr(Float32),
    D: Addr(Float32),
    RT1R: Addr(Float32),
    RT1I: Addr(Float32),
    RT2R: Addr(Float32),
    RT2I: Addr(Float32),
    CS: Addr(Float32),
    SN: Addr(Float32)
) -> None: ...

@bind("SLAORHR_COL_GETRFNP")
@external
def slaorhr_col_getrfnp(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAORHR_COL_GETRFNP2")
@external
def slaorhr_col_getrfnp2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAPLL")
@external
def slapll(
    N: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    Y: Float32[Flat],
    INCY: Addr(Int32),
    SSMIN: Addr(Float32)
) -> None: ...

@bind("SLAPMR")
@external
def slapmr(
    FORWRD: Addr(Bool),
    M: Addr(Int32),
    N: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("SLAPMT")
@external
def slapmt(
    FORWRD: Addr(Bool),
    M: Addr(Int32),
    N: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("SLAPY2")
@external
def slapy2(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("SLAPY3")
@external
def slapy3(
    X: Addr(Float32),
    Y: Addr(Float32),
    Z: Addr(Float32)
) -> Float32: ...

@bind("SLAQGB")
@external
def slaqgb(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("SLAQGE")
@external
def slaqge(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Addr(Float32),
    COLCND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("SLAQP2")
@external
def slaqp2(
    M: Addr(Int32),
    N: Addr(Int32),
    OFFSET: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Float32[Flat]
) -> None: ...

@bind("SLAQP2RK")
@external
def slaqp2rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    IOFFSET: Addr(Int32),
    KMAX: Addr(Int32),
    ABSTOL: Addr(Float32),
    RELTOL: Addr(Float32),
    KP1: Addr(Int32),
    MAXC2NRM: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    K: Addr(Int32),
    MAXC2NRMK: Addr(Float32),
    RELMAXC2NRMK: Addr(Float32),
    JPIV: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAQP3RK")
@external
def slaqp3rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    IOFFSET: Addr(Int32),
    NB: Addr(Int32),
    ABSTOL: Addr(Float32),
    RELTOL: Addr(Float32),
    KP1: Addr(Int32),
    MAXC2NRM: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    DONE: Addr(Bool),
    KB: Addr(Int32),
    MAXC2NRMK: Addr(Float32),
    RELMAXC2NRMK: Addr(Float32),
    JPIV: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Float32[Flat],
    F: Float32[LDF, Flat],
    LDF: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAQPS")
@external
def slaqps(
    M: Addr(Int32),
    N: Addr(Int32),
    OFFSET: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Float32[Flat],
    F: Float32[LDF, Flat],
    LDF: Addr(Int32)
) -> None: ...

@bind("SLAQR0")
@external
def slaqr0(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAQR1")
@external
def slaqr1(
    N: Addr(Int32),
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    SR1: Addr(Float32),
    SI1: Addr(Float32),
    SR2: Addr(Float32),
    SI2: Addr(Float32),
    V: Float32[Flat]
) -> None: ...

@bind("SLAQR2")
@external
def slaqr2(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NW: Addr(Int32),
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    NS: Addr(Int32),
    ND: Addr(Int32),
    SR: Float32[Flat],
    SI: Float32[Flat],
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    NH: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    NV: Addr(Int32),
    WV: Float32[LDWV, Flat],
    LDWV: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32)
) -> None: ...

@bind("SLAQR3")
@external
def slaqr3(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NW: Addr(Int32),
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    NS: Addr(Int32),
    ND: Addr(Int32),
    SR: Float32[Flat],
    SI: Float32[Flat],
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    NH: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    NV: Addr(Int32),
    WV: Float32[LDWV, Flat],
    LDWV: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32)
) -> None: ...

@bind("SLAQR4")
@external
def slaqr4(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAQR5")
@external
def slaqr5(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    KACC22: Addr(Int32),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NSHFTS: Addr(Int32),
    SR: Float32[Flat],
    SI: Float32[Flat],
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    NV: Addr(Int32),
    WV: Float32[LDWV, Flat],
    LDWV: Addr(Int32),
    NH: Addr(Int32),
    WH: Float32[LDWH, Flat],
    LDWH: Addr(Int32)
) -> None: ...

@bind("SLAQSB")
@external
def slaqsb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("SLAQSP")
@external
def slaqsp(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("SLAQSY")
@external
def slaqsy(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("SLAQTR")
@external
def slaqtr(
    LTRAN: Addr(Bool),
    LREAL: Addr(Bool),
    N: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    B: Float32[Flat],
    W: Addr(Float32),
    SCALE: Addr(Float32),
    X: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Arg(10), Arg(11), Arg(12), Arg(13), Addr(Arg(14)), Arg(15), Addr(Arg(16)), Arg(17), Addr(Arg(18)), Addr(Arg(19)), Return('INFO', 0)])
def slaqz0(
    WANTS: Addr(Const(String[1])),
    WANTQ: Addr(Const(String[1])),
    WANTZ: Addr(Const(String[1])),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    A: Float32[LDA, Flat],
    LDA: Const(Int32),
    B: Float32[LDB, Flat],
    LDB: Const(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Const(Int32),
    WORK: Float32[Flat],
    LWORK: Const(Int32),
    REC: Const(Int32)
) -> Int32: ...

@bind("SLAQZ1")
@external
@native_call([Arg(0), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Addr(Arg(7)), Addr(Arg(8)), Arg(9)])
def slaqz1(
    A: Const(Float32[LDA, Flat]),
    LDA: Const(Int32),
    B: Const(Float32[LDB, Flat]),
    LDB: Const(Int32),
    SR1: Const(Float32),
    SR2: Const(Float32),
    SI: Const(Float32),
    BETA1: Const(Float32),
    BETA2: Const(Float32),
    V: Float32[Flat]
) -> Returns["V", Float32[Flat]]: ...

@bind("SLAQZ2")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Addr(Arg(11)), Arg(12), Addr(Arg(13)), Addr(Arg(14)), Addr(Arg(15)), Arg(16), Addr(Arg(17))])
def slaqz2(
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    K: Const(Int32),
    ISTARTM: Const(Int32),
    ISTOPM: Const(Int32),
    IHI: Const(Int32),
    A: Float32[LDA, Flat],
    LDA: Const(Int32),
    B: Float32[LDB, Flat],
    LDB: Const(Int32),
    NQ: Const(Int32),
    QSTART: Const(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Const(Int32),
    NZ: Const(Int32),
    ZSTART: Const(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Const(Int32)
) -> None: ...

@bind("SLAQZ3")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Arg(11), Addr(Arg(12)), Arg(13), Addr(Arg(14)), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Arg(18), Addr(Arg(19)), Arg(20), Addr(Arg(21)), Arg(22), Addr(Arg(23)), Addr(Arg(24)), Return('INFO', 2)])
def slaqz3(
    ILSCHUR: Const(Bool),
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    NW: Const(Int32),
    A: Float32[LDA, Flat],
    LDA: Const(Int32),
    B: Float32[LDB, Flat],
    LDB: Const(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Const(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    QC: Float32[LDQC, Flat],
    LDQC: Const(Int32),
    ZC: Float32[LDZC, Flat],
    LDZC: Const(Int32),
    WORK: Float32[Flat],
    LWORK: Const(Int32),
    REC: Const(Int32)
) -> tuple[Int32, Int32, Int32]: ...

@bind("SLAQZ4")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Arg(9), Arg(10), Arg(11), Addr(Arg(12)), Arg(13), Addr(Arg(14)), Arg(15), Addr(Arg(16)), Arg(17), Addr(Arg(18)), Arg(19), Addr(Arg(20)), Arg(21), Addr(Arg(22)), Arg(23), Addr(Arg(24)), Return('INFO', 0)])
def slaqz4(
    ILSCHUR: Const(Bool),
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    NSHIFTS: Const(Int32),
    NBLOCK_DESIRED: Const(Int32),
    SR: Float32[Flat],
    SI: Float32[Flat],
    SS: Float32[Flat],
    A: Float32[LDA, Flat],
    LDA: Const(Int32),
    B: Float32[LDB, Flat],
    LDB: Const(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Const(Int32),
    QC: Float32[LDQC, Flat],
    LDQC: Const(Int32),
    ZC: Float32[LDZC, Flat],
    LDZC: Const(Int32),
    WORK: Float32[Flat],
    LWORK: Const(Int32)
) -> Int32: ...

@bind("SLAR1V")
@external
def slar1v(
    N: Addr(Int32),
    B1: Addr(Int32),
    BN: Addr(Int32),
    LAMBDA: Addr(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    LD: Float32[Flat],
    LLD: Float32[Flat],
    PIVMIN: Addr(Float32),
    GAPTOL: Addr(Float32),
    Z: Float32[Flat],
    WANTNC: Addr(Bool),
    NEGCNT: Addr(Int32),
    ZTZ: Addr(Float32),
    MINGMA: Addr(Float32),
    R: Addr(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Addr(Float32),
    RESID: Addr(Float32),
    RQCORR: Addr(Float32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLAR2V")
@external
def slar2v(
    N: Addr(Int32),
    X: Float32[Flat],
    Y: Float32[Flat],
    Z: Float32[Flat],
    INCX: Addr(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("SLARF")
@external
def slarf(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Float32[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARF1F")
@external
def slarf1f(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Float32[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARF1L")
@external
def slarf1l(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Float32[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARFB")
@external
def slarfb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("SLARFB_GETT")
@external
def slarfb_gett(
    IDENT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("SLARFG")
@external
def slarfg(
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    TAU: Addr(Float32)
) -> None: ...

@bind("SLARFGP")
@external
def slarfgp(
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    TAU: Addr(Float32)
) -> None: ...

@bind("SLARFT")
@external
def slarft(
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    TAU: Float32[Flat],
    T: Float32[LDT, Flat],
    LDT: Addr(Int32)
) -> None: ...

@bind("SLARFX")
@external
def slarfx(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Float32[Flat],
    TAU: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARFY")
@external
def slarfy(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    V: Float32[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARGV")
@external
def slargv(
    N: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    Y: Float32[Flat],
    INCY: Addr(Int32),
    C: Float32[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("SLARMM")
@external
def slarmm(
    ANORM: Addr(Float32),
    BNORM: Addr(Float32),
    CNORM: Addr(Float32)
) -> Float32: ...

@bind("SLARNV")
@external
def slarnv(
    IDIST: Addr(Int32),
    ISEED: Int32[4],
    N: Addr(Int32),
    X: Float32[Flat]
) -> None: ...

@bind("SLARRA")
@external
def slarra(
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    SPLTOL: Addr(Float32),
    TNRM: Addr(Float32),
    NSPLIT: Addr(Int32),
    ISPLIT: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLARRB")
@external
def slarrb(
    N: Addr(Int32),
    D: Float32[Flat],
    LLD: Float32[Flat],
    IFIRST: Addr(Int32),
    ILAST: Addr(Int32),
    RTOL1: Addr(Float32),
    RTOL2: Addr(Float32),
    OFFSET: Addr(Int32),
    W: Float32[Flat],
    WGAP: Float32[Flat],
    WERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Addr(Float32),
    SPDIAM: Addr(Float32),
    TWIST: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLARRC")
@external
def slarrc(
    JOBT: Addr(Const(String[1])),
    N: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    PIVMIN: Addr(Float32),
    EIGCNT: Addr(Int32),
    LCNT: Addr(Int32),
    RCNT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLARRD")
@external
def slarrd(
    RANGE: Addr(Const(String[1])),
    ORDER: Addr(Const(String[1])),
    N: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    GERS: Float32[Flat],
    RELTOL: Addr(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    PIVMIN: Addr(Float32),
    NSPLIT: Addr(Int32),
    ISPLIT: Int32[Flat],
    M: Addr(Int32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WL: Addr(Float32),
    WU: Addr(Float32),
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLARRE")
@external
def slarre(
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    RTOL1: Addr(Float32),
    RTOL2: Addr(Float32),
    SPLTOL: Addr(Float32),
    NSPLIT: Addr(Int32),
    ISPLIT: Int32[Flat],
    M: Addr(Int32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WGAP: Float32[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float32[Flat],
    PIVMIN: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLARRF")
@external
def slarrf(
    N: Addr(Int32),
    D: Float32[Flat],
    L: Float32[Flat],
    LD: Float32[Flat],
    CLSTRT: Addr(Int32),
    CLEND: Addr(Int32),
    W: Float32[Flat],
    WGAP: Float32[Flat],
    WERR: Float32[Flat],
    SPDIAM: Addr(Float32),
    CLGAPL: Addr(Float32),
    CLGAPR: Addr(Float32),
    PIVMIN: Addr(Float32),
    SIGMA: Addr(Float32),
    DPLUS: Float32[Flat],
    LPLUS: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLARRJ")
@external
def slarrj(
    N: Addr(Int32),
    D: Float32[Flat],
    E2: Float32[Flat],
    IFIRST: Addr(Int32),
    ILAST: Addr(Int32),
    RTOL: Addr(Float32),
    OFFSET: Addr(Int32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Addr(Float32),
    SPDIAM: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLARRK")
@external
def slarrk(
    N: Addr(Int32),
    IW: Addr(Int32),
    GL: Addr(Float32),
    GU: Addr(Float32),
    D: Float32[Flat],
    E2: Float32[Flat],
    PIVMIN: Addr(Float32),
    RELTOL: Addr(Float32),
    W: Addr(Float32),
    WERR: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLARRR")
@external
def slarrr(
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLARRV")
@external
def slarrv(
    N: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    PIVMIN: Addr(Float32),
    ISPLIT: Int32[Flat],
    M: Addr(Int32),
    DOL: Addr(Int32),
    DOU: Addr(Int32),
    MINRGP: Addr(Float32),
    RTOL1: Addr(Float32),
    RTOL2: Addr(Float32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WGAP: Float32[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLARSCL2")
@external
def slarscl2(
    M: Addr(Int32),
    N: Addr(Int32),
    D: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Addr(Int32)
) -> None: ...

@bind("SLARTG")
@external
def slartg(
    f: Addr(Float32),
    g: Addr(Float32),
    c: Addr(Float32),
    s: Addr(Float32),
    r: Addr(Float32)
) -> None: ...

@bind("SLARTGP")
@external
def slartgp(
    F: Addr(Float32),
    G: Addr(Float32),
    CS: Addr(Float32),
    SN: Addr(Float32),
    R: Addr(Float32)
) -> None: ...

@bind("SLARTGS")
@external
def slartgs(
    X: Addr(Float32),
    Y: Addr(Float32),
    SIGMA: Addr(Float32),
    CS: Addr(Float32),
    SN: Addr(Float32)
) -> None: ...

@bind("SLARTV")
@external
def slartv(
    N: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    Y: Float32[Flat],
    INCY: Addr(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("SLARUV")
@external
def slaruv(
    ISEED: Int32[4],
    N: Addr(Int32),
    X: Float32[N]
) -> None: ...

@bind("SLARZ")
@external
def slarz(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    V: Float32[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARZB")
@external
def slarzb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("SLARZT")
@external
def slarzt(
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    TAU: Float32[Flat],
    T: Float32[LDT, Flat],
    LDT: Addr(Int32)
) -> None: ...

@bind("SLAS2")
@external
def slas2(
    F: Addr(Float32),
    G: Addr(Float32),
    H: Addr(Float32),
    SSMIN: Addr(Float32),
    SSMAX: Addr(Float32)
) -> None: ...

@bind("SLASCL")
@external
def slascl(
    TYPE: Addr(Const(String[1])),
    KL: Addr(Int32),
    KU: Addr(Int32),
    CFROM: Addr(Float32),
    CTO: Addr(Float32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASCL2")
@external
def slascl2(
    M: Addr(Int32),
    N: Addr(Int32),
    D: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Addr(Int32)
) -> None: ...

@bind("SLASD0")
@external
def slasd0(
    N: Addr(Int32),
    SQRE: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Addr(Int32),
    SMLSIZ: Addr(Int32),
    IWORK: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASD1")
@external
def slasd1(
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    D: Float32[Flat],
    ALPHA: Addr(Float32),
    BETA: Addr(Float32),
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Addr(Int32),
    IDXQ: Int32[Flat],
    IWORK: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASD2")
@external
def slasd2(
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    K: Addr(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    ALPHA: Addr(Float32),
    BETA: Addr(Float32),
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Addr(Int32),
    DSIGMA: Float32[Flat],
    U2: Float32[LDU2, Flat],
    LDU2: Addr(Int32),
    VT2: Float32[LDVT2, Flat],
    LDVT2: Addr(Int32),
    IDXP: Int32[Flat],
    IDX: Int32[Flat],
    IDXC: Int32[Flat],
    IDXQ: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASD3")
@external
def slasd3(
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    K: Addr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    DSIGMA: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Addr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Addr(Int32),
    VT2: Float32[LDVT2, Flat],
    LDVT2: Addr(Int32),
    IDXC: Int32[Flat],
    CTOT: Int32[Flat],
    Z: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASD4")
@external
def slasd4(
    N: Addr(Int32),
    I: Addr(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    DELTA: Float32[Flat],
    RHO: Addr(Float32),
    SIGMA: Addr(Float32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASD5")
@external
def slasd5(
    I: Addr(Int32),
    D: Float32[2],
    Z: Float32[2],
    DELTA: Float32[2],
    RHO: Addr(Float32),
    DSIGMA: Addr(Float32),
    WORK: Float32[2]
) -> None: ...

@bind("SLASD6")
@external
def slasd6(
    ICOMPQ: Addr(Int32),
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    D: Float32[Flat],
    VF: Float32[Flat],
    VL: Float32[Flat],
    ALPHA: Addr(Float32),
    BETA: Addr(Float32),
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Addr(Int32),
    POLES: Float32[LDGNUM, Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[Flat],
    Z: Float32[Flat],
    K: Addr(Int32),
    C: Addr(Float32),
    S: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASD7")
@external
def slasd7(
    ICOMPQ: Addr(Int32),
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    K: Addr(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    ZW: Float32[Flat],
    VF: Float32[Flat],
    VFW: Float32[Flat],
    VL: Float32[Flat],
    VLW: Float32[Flat],
    ALPHA: Addr(Float32),
    BETA: Addr(Float32),
    DSIGMA: Float32[Flat],
    IDX: Int32[Flat],
    IDXP: Int32[Flat],
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Addr(Int32),
    C: Addr(Float32),
    S: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASD8")
@external
def slasd8(
    ICOMPQ: Addr(Int32),
    K: Addr(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    VF: Float32[Flat],
    VL: Float32[Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[LDDIFR, Flat],
    LDDIFR: Addr(Int32),
    DSIGMA: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASDA")
@external
def slasda(
    ICOMPQ: Addr(Int32),
    SMLSIZ: Addr(Int32),
    N: Addr(Int32),
    SQRE: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float32[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float32[LDU, Flat],
    DIFR: Float32[LDU, Flat],
    Z: Float32[LDU, Flat],
    POLES: Float32[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float32[LDU, Flat],
    C: Float32[Flat],
    S: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASDQ")
@external
def slasdq(
    UPLO: Addr(Const(String[1])),
    SQRE: Addr(Int32),
    N: Addr(Int32),
    NCVT: Addr(Int32),
    NRU: Addr(Int32),
    NCC: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VT: Float32[LDVT, Flat],
    LDVT: Addr(Int32),
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASDT")
@external
def slasdt(
    N: Addr(Int32),
    LVL: Addr(Int32),
    ND: Addr(Int32),
    INODE: Int32[Flat],
    NDIML: Int32[Flat],
    NDIMR: Int32[Flat],
    MSUB: Addr(Int32)
) -> None: ...

@bind("SLASET")
@external
def slaset(
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    BETA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("SLASQ1")
@external
def slasq1(
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASQ2")
@external
def slasq2(
    N: Addr(Int32),
    Z: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASQ3")
@external
def slasq3(
    I0: Addr(Int32),
    N0: Addr(Int32),
    Z: Float32[Flat],
    PP: Addr(Int32),
    DMIN: Addr(Float32),
    SIGMA: Addr(Float32),
    DESIG: Addr(Float32),
    QMAX: Addr(Float32),
    NFAIL: Addr(Int32),
    ITER: Addr(Int32),
    NDIV: Addr(Int32),
    IEEE: Addr(Bool),
    TTYPE: Addr(Int32),
    DMIN1: Addr(Float32),
    DMIN2: Addr(Float32),
    DN: Addr(Float32),
    DN1: Addr(Float32),
    DN2: Addr(Float32),
    G: Addr(Float32),
    TAU: Addr(Float32)
) -> None: ...

@bind("SLASQ4")
@external
def slasq4(
    I0: Addr(Int32),
    N0: Addr(Int32),
    Z: Float32[Flat],
    PP: Addr(Int32),
    N0IN: Addr(Int32),
    DMIN: Addr(Float32),
    DMIN1: Addr(Float32),
    DMIN2: Addr(Float32),
    DN: Addr(Float32),
    DN1: Addr(Float32),
    DN2: Addr(Float32),
    TAU: Addr(Float32),
    TTYPE: Addr(Int32),
    G: Addr(Float32)
) -> None: ...

@bind("SLASQ5")
@external
def slasq5(
    I0: Addr(Int32),
    N0: Addr(Int32),
    Z: Float32[Flat],
    PP: Addr(Int32),
    TAU: Addr(Float32),
    SIGMA: Addr(Float32),
    DMIN: Addr(Float32),
    DMIN1: Addr(Float32),
    DMIN2: Addr(Float32),
    DN: Addr(Float32),
    DNM1: Addr(Float32),
    DNM2: Addr(Float32),
    IEEE: Addr(Bool),
    EPS: Addr(Float32)
) -> None: ...

@bind("SLASQ6")
@external
def slasq6(
    I0: Addr(Int32),
    N0: Addr(Int32),
    Z: Float32[Flat],
    PP: Addr(Int32),
    DMIN: Addr(Float32),
    DMIN1: Addr(Float32),
    DMIN2: Addr(Float32),
    DN: Addr(Float32),
    DNM1: Addr(Float32),
    DNM2: Addr(Float32)
) -> None: ...

@bind("SLASR")
@external
def slasr(
    SIDE: Addr(Const(String[1])),
    PIVOT: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    A: Float32[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("SLASRT")
@external
def slasrt(
    ID: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASSQ")
@external
def slassq(
    n: Addr(Int32),
    x: Float32[Flat],
    incx: Addr(Int32),
    scale: Addr(Float32),
    sumsq: Addr(Float32)
) -> None: ...

@bind("SLASV2")
@external
def slasv2(
    F: Addr(Float32),
    G: Addr(Float32),
    H: Addr(Float32),
    SSMIN: Addr(Float32),
    SSMAX: Addr(Float32),
    SNR: Addr(Float32),
    CSR: Addr(Float32),
    SNL: Addr(Float32),
    CSL: Addr(Float32)
) -> None: ...

@bind("SLASWLQ")
@external
def slaswlq(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASWP")
@external
def slaswp(
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    K1: Addr(Int32),
    K2: Addr(Int32),
    IPIV: Int32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("SLASY2")
@external
def slasy2(
    LTRANL: Addr(Bool),
    LTRANR: Addr(Bool),
    ISGN: Addr(Int32),
    N1: Addr(Int32),
    N2: Addr(Int32),
    TL: Float32[LDTL, Flat],
    LDTL: Addr(Int32),
    TR: Float32[LDTR, Flat],
    LDTR: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    SCALE: Addr(Float32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    XNORM: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASYF")
@external
def slasyf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Float32[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASYF_AA")
@external
def slasyf_aa(
    UPLO: Addr(Const(String[1])),
    J1: Addr(Int32),
    M: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    H: Float32[LDH, Flat],
    LDH: Addr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLASYF_RK")
@external
def slasyf_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    W: Float32[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLASYF_ROOK")
@external
def slasyf_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Float32[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLATBS")
@external
def slatbs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    X: Float32[Flat],
    SCALE: Addr(Float32),
    CNORM: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLATDF")
@external
def slatdf(
    IJOB: Addr(Int32),
    N: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    RHS: Float32[Flat],
    RDSUM: Addr(Float32),
    RDSCAL: Addr(Float32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("SLATPS")
@external
def slatps(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    X: Float32[Flat],
    SCALE: Addr(Float32),
    CNORM: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLATRD")
@external
def slatrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    TAU: Float32[Flat],
    W: Float32[LDW, Flat],
    LDW: Addr(Int32)
) -> None: ...

@bind("SLATRS")
@external
def slatrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    X: Float32[Flat],
    SCALE: Addr(Float32),
    CNORM: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SLATRS3")
@external
def slatrs3(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    SCALE: Float32[Flat],
    CNORM: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLATRZ")
@external
def slatrz(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat]
) -> None: ...

@bind("SLATSQR")
@external
def slatsqr(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAUU2")
@external
def slauu2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SLAUUM")
@external
def slauum(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SOPGTR")
@external
def sopgtr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    TAU: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SOPMTR")
@external
def sopmtr(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    AP: Float32[Flat],
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORBDB")
@external
def sorbdb(
    TRANS: Addr(Const(String[1])),
    SIGNS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Addr(Int32),
    X12: Float32[LDX12, Flat],
    LDX12: Addr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Addr(Int32),
    X22: Float32[LDX22, Flat],
    LDX22: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    TAUQ2: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORBDB1")
@external
def sorbdb1(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORBDB2")
@external
def sorbdb2(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORBDB3")
@external
def sorbdb3(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORBDB4")
@external
def sorbdb4(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    PHANTOM: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORBDB5")
@external
def sorbdb5(
    M1: Addr(Int32),
    M2: Addr(Int32),
    N: Addr(Int32),
    X1: Float32[Flat],
    INCX1: Addr(Int32),
    X2: Float32[Flat],
    INCX2: Addr(Int32),
    Q1: Float32[LDQ1, Flat],
    LDQ1: Addr(Int32),
    Q2: Float32[LDQ2, Flat],
    LDQ2: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORBDB6")
@external
def sorbdb6(
    M1: Addr(Int32),
    M2: Addr(Int32),
    N: Addr(Int32),
    X1: Float32[Flat],
    INCX1: Addr(Int32),
    X2: Float32[Flat],
    INCX2: Addr(Int32),
    Q1: Float32[LDQ1, Flat],
    LDQ1: Addr(Int32),
    Q2: Float32[LDQ2, Flat],
    LDQ2: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORCSD")
@external
def sorcsd(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    JOBV2T: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    SIGNS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Addr(Int32),
    X12: Float32[LDX12, Flat],
    LDX12: Addr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Addr(Int32),
    X22: Float32[LDX22, Flat],
    LDX22: Addr(Int32),
    THETA: Float32[Flat],
    U1: Float32[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Float32[LDV1T, Flat],
    LDV1T: Addr(Int32),
    V2T: Float32[LDV2T, Flat],
    LDV2T: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORCSD2BY1")
@external
def sorcsd2by1(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float32[Flat],
    U1: Float32[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Float32[LDV1T, Flat],
    LDV1T: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORG2L")
@external
def sorg2l(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORG2R")
@external
def sorg2r(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGBR")
@external
def sorgbr(
    VECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGHR")
@external
def sorghr(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGL2")
@external
def sorgl2(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGLQ")
@external
def sorglq(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGQL")
@external
def sorgql(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGQR")
@external
def sorgqr(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGR2")
@external
def sorgr2(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGRQ")
@external
def sorgrq(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGTR")
@external
def sorgtr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGTSQR")
@external
def sorgtsqr(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORGTSQR_ROW")
@external
def sorgtsqr_row(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORHR_COL")
@external
def sorhr_col(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    D: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORM22")
@external
def sorm22(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    N2: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORM2L")
@external
def sorm2l(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORM2R")
@external
def sorm2r(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORMBR")
@external
def sormbr(
    VECT: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORMHR")
@external
def sormhr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORML2")
@external
def sorml2(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORMLQ")
@external
def sormlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORMQL")
@external
def sormql(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORMQR")
@external
def sormqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORMR2")
@external
def sormr2(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORMR3")
@external
def sormr3(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SORMRQ")
@external
def sormrq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORMRZ")
@external
def sormrz(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SORMTR")
@external
def sormtr(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPBCON")
@external
def spbcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPBEQU")
@external
def spbequ(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPBRFS")
@external
def spbrfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPBSTF")
@external
def spbstf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPBSV")
@external
def spbsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPBSVX")
@external
def spbsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPBTF2")
@external
def spbtf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPBTRF")
@external
def spbtrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPBTRS")
@external
def spbtrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPFTRF")
@external
def spftrf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPFTRI")
@external
def spftri(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPFTRS")
@external
def spftrs(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOCON")
@external
def spocon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOEQU")
@external
def spoequ(
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOEQUB")
@external
def spoequb(
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPORFS")
@external
def sporfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPORFSX")
@external
def sporfsx(
    UPLO: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOSV")
@external
def sposv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOSVX")
@external
def sposvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOSVXX")
@external
def sposvxx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    RPVGRW: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOTF2")
@external
def spotf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOTRF")
@external
def spotrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOTRF2")
@external
def spotrf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOTRI")
@external
def spotri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPOTRS")
@external
def spotrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPPCON")
@external
def sppcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPPEQU")
@external
def sppequ(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPPRFS")
@external
def spprfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPPSV")
@external
def sppsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPPSVX")
@external
def sppsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPPTRF")
@external
def spptrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPPTRI")
@external
def spptri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPPTRS")
@external
def spptrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPSTF2")
@external
def spstf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    PIV: Int32[N],
    RANK: Addr(Int32),
    TOL: Addr(Float32),
    WORK: Float32[2 * N],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPSTRF")
@external
def spstrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    PIV: Int32[N],
    RANK: Addr(Int32),
    TOL: Addr(Float32),
    WORK: Float32[2 * N],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPTCON")
@external
def sptcon(
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPTEQR")
@external
def spteqr(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPTRFS")
@external
def sptrfs(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    DF: Float32[Flat],
    EF: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPTSV")
@external
def sptsv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPTSVX")
@external
def sptsvx(
    FACT: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    DF: Float32[Flat],
    EF: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPTTRF")
@external
def spttrf(
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SPTTRS")
@external
def spttrs(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SPTTS2")
@external
def sptts2(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("SRSCL")
@external
def srscl(
    N: Addr(Int32),
    SA: Addr(Float32),
    SX: Float32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("SSB2ST_KERNELS")
@external
def ssb2st_kernels(
    UPLO: Addr(Const(String[1])),
    WANTZ: Addr(Bool),
    TTYPE: Addr(Int32),
    ST: Addr(Int32),
    ED: Addr(Int32),
    SWEEP: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    IB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    V: Float32[Flat],
    TAU: Float32[Flat],
    LDVT: Addr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SSBEV")
@external
def ssbev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSBEV_2STAGE")
@external
def ssbev_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSBEVD")
@external
def ssbevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSBEVD_2STAGE")
@external
def ssbevd_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSBEVX")
@external
def ssbevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSBEVX_2STAGE")
@external
def ssbevx_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSBGST")
@external
def ssbgst(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSBGV")
@external
def ssbgv(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSBGVD")
@external
def ssbgvd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSBGVX")
@external
def ssbgvx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSBTRD")
@external
def ssbtrd(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSFRK")
@external
def ssfrk(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    BETA: Addr(Float32),
    C: Float32[Flat]
) -> None: ...

@bind("SSPCON")
@external
def sspcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPEV")
@external
def sspev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPEVD")
@external
def sspevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPEVX")
@external
def sspevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPGST")
@external
def sspgst(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPGV")
@external
def sspgv(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPGVD")
@external
def sspgvd(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPGVX")
@external
def sspgvx(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPRFS")
@external
def ssprfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPSV")
@external
def sspsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPSVX")
@external
def sspsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPTRD")
@external
def ssptrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPTRF")
@external
def ssptrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPTRI")
@external
def ssptri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSPTRS")
@external
def ssptrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTEBZ")
@external
def sstebz(
    RANGE: Addr(Const(String[1])),
    ORDER: Addr(Const(String[1])),
    N: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    M: Addr(Int32),
    NSPLIT: Addr(Int32),
    W: Float32[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTEDC")
@external
def sstedc(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTEGR")
@external
def sstegr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTEIN")
@external
def sstein(
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    M: Addr(Int32),
    W: Float32[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTEMR")
@external
def sstemr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    NZC: Addr(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Addr(Bool),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTEQR")
@external
def ssteqr(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTERF")
@external
def ssterf(
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTEV")
@external
def sstev(
    JOBZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTEVD")
@external
def sstevd(
    JOBZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTEVR")
@external
def sstevr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSTEVX")
@external
def sstevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYCON")
@external
def ssycon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYCON_3")
@external
def ssycon_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYCON_ROOK")
@external
def ssycon_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYCONV")
@external
def ssyconv(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    E: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYCONVF")
@external
def ssyconvf(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYCONVF_ROOK")
@external
def ssyconvf_rook(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYEQUB")
@external
def ssyequb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    S: Float32[Flat],
    SCOND: Addr(Float32),
    AMAX: Addr(Float32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYEV")
@external
def ssyev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYEV_2STAGE")
@external
def ssyev_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYEVD")
@external
def ssyevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYEVD_2STAGE")
@external
def ssyevd_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYEVR")
@external
def ssyevr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYEVR_2STAGE")
@external
def ssyevr_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYEVX")
@external
def ssyevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYEVX_2STAGE")
@external
def ssyevx_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYGS2")
@external
def ssygs2(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYGST")
@external
def ssygst(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYGV")
@external
def ssygv(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYGV_2STAGE")
@external
def ssygv_2stage(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYGVD")
@external
def ssygvd(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYGVX")
@external
def ssygvx(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    VL: Addr(Float32),
    VU: Addr(Float32),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float32),
    M: Addr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYRFS")
@external
def ssyrfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYRFSX")
@external
def ssyrfsx(
    UPLO: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYSV")
@external
def ssysv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYSV_AA")
@external
def ssysv_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYSV_AA_2STAGE")
@external
def ssysv_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TB: Float32[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYSV_RK")
@external
def ssysv_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYSV_ROOK")
@external
def ssysv_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYSVX")
@external
def ssysvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYSVXX")
@external
def ssysvxx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float32),
    RPVGRW: Addr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYSWAPR")
@external
def ssyswapr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    I1: Addr(Int32),
    I2: Addr(Int32)
) -> None: ...

@bind("SSYTD2")
@external
def ssytd2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTF2")
@external
def ssytf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTF2_RK")
@external
def ssytf2_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTF2_ROOK")
@external
def ssytf2_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRD")
@external
def ssytrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRD_2STAGE")
@external
def ssytrd_2stage(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    HOUS2: Float32[Flat],
    LHOUS2: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRD_SB2ST")
@external
def ssytrd_sb2st(
    STAGE1: Addr(Const(String[1])),
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    HOUS: Float32[Flat],
    LHOUS: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRD_SY2SB")
@external
def ssytrd_sy2sb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRF")
@external
def ssytrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRF_AA")
@external
def ssytrf_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRF_AA_2STAGE")
@external
def ssytrf_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TB: Float32[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRF_RK")
@external
def ssytrf_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRF_ROOK")
@external
def ssytrf_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRI")
@external
def ssytri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRI2")
@external
def ssytri2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRI2X")
@external
def ssytri2x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRI_3")
@external
def ssytri_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRI_3X")
@external
def ssytri_3x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRI_ROOK")
@external
def ssytri_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRS")
@external
def ssytrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRS2")
@external
def ssytrs2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRS_3")
@external
def ssytrs_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRS_AA")
@external
def ssytrs_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRS_AA_2STAGE")
@external
def ssytrs_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TB: Float32[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("SSYTRS_ROOK")
@external
def ssytrs_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STBCON")
@external
def stbcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STBRFS")
@external
def stbrfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STBTRS")
@external
def stbtrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STFSM")
@external
def stfsm(
    TRANSR: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    B: Annotated[Float32[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Addr(Int32)
) -> None: ...

@bind("STFTRI")
@external
def stftri(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("STFTTP")
@external
def stfttp(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    AP: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("STFTTR")
@external
def stfttr(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    A: Annotated[Float32[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STGEVC")
@external
def stgevc(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    S: Float32[LDS, Flat],
    LDS: Addr(Int32),
    P: Float32[LDP, Flat],
    LDP: Addr(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STGEX2")
@external
def stgex2(
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    J1: Addr(Int32),
    N1: Addr(Int32),
    N2: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STGEXC")
@external
def stgexc(
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    IFST: Addr(Int32),
    ILST: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STGSEN")
@external
def stgsen(
    IJOB: Addr(Int32),
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Addr(Int32),
    M: Addr(Int32),
    PL: Addr(Float32),
    PR: Addr(Float32),
    DIF: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STGSJA")
@external
def stgsja(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    TOLA: Addr(Float32),
    TOLB: Addr(Float32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Float32[Flat],
    NCYCLE: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STGSNA")
@external
def stgsna(
    JOB: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    S: Float32[Flat],
    DIF: Float32[Flat],
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STGSY2")
@external
def stgsy2(
    TRANS: Addr(Const(String[1])),
    IJOB: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    D: Float32[LDD, Flat],
    LDD: Addr(Int32),
    E: Float32[LDE, Flat],
    LDE: Addr(Int32),
    F: Float32[LDF, Flat],
    LDF: Addr(Int32),
    SCALE: Addr(Float32),
    RDSUM: Addr(Float32),
    RDSCAL: Addr(Float32),
    IWORK: Int32[Flat],
    PQ: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STGSYL")
@external
def stgsyl(
    TRANS: Addr(Const(String[1])),
    IJOB: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    D: Float32[LDD, Flat],
    LDD: Addr(Int32),
    E: Float32[LDE, Flat],
    LDE: Addr(Int32),
    F: Float32[LDF, Flat],
    LDF: Addr(Int32),
    SCALE: Addr(Float32),
    DIF: Addr(Float32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STPCON")
@external
def stpcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STPLQT")
@external
def stplqt(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    MB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STPLQT2")
@external
def stplqt2(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STPMLQT")
@external
def stpmlqt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    MB: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STPMQRT")
@external
def stpmqrt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    NB: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STPQRT")
@external
def stpqrt(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    NB: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STPQRT2")
@external
def stpqrt2(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STPRFB")
@external
def stprfb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    V: Float32[LDV, Flat],
    LDV: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("STPRFS")
@external
def stprfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STPTRI")
@external
def stptri(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STPTRS")
@external
def stptrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STPTTF")
@external
def stpttf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Annotated[Float32[Flat], SourceDims("0:*")],
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("STPTTR")
@external
def stpttr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STRCON")
@external
def strcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    RCOND: Addr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STREVC")
@external
def strevc(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STREVC3")
@external
def strevc3(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STREXC")
@external
def strexc(
    COMPQ: Addr(Const(String[1])),
    N: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    IFST: Addr(Int32),
    ILST: Addr(Int32),
    WORK: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STRRFS")
@external
def strrfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    X: Float32[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STRSEN")
@external
def strsen(
    JOB: Addr(Const(String[1])),
    COMPQ: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Addr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    M: Addr(Int32),
    S: Addr(Float32),
    SEP: Addr(Float32),
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STRSNA")
@external
def strsna(
    JOB: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Float32[LDT, Flat],
    LDT: Addr(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Addr(Int32),
    S: Float32[Flat],
    SEP: Float32[Flat],
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STRSYL")
@external
def strsyl(
    TRANA: Addr(Const(String[1])),
    TRANB: Addr(Const(String[1])),
    ISGN: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    SCALE: Addr(Float32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STRSYL3")
@external
def strsyl3(
    TRANA: Addr(Const(String[1])),
    TRANB: Addr(Const(String[1])),
    ISGN: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32),
    SCALE: Addr(Float32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    SWORK: Float32[LDSWORK, Flat],
    LDSWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STRTI2")
@external
def strti2(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STRTRI")
@external
def strtri(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STRTRS")
@external
def strtrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("STRTTF")
@external
def strttf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Float32[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Addr(Int32),
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("STRTTP")
@external
def strttp(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    AP: Float32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("STZRZF")
@external
def stzrzf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
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

@bind("ZBBCSD")
@external
def zbbcsd(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    JOBV2T: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    U1: Complex128[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Complex128[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Complex128[LDV1T, Flat],
    LDV1T: Addr(Int32),
    V2T: Complex128[LDV2T, Flat],
    LDV2T: Addr(Int32),
    B11D: Float64[Flat],
    B11E: Float64[Flat],
    B12D: Float64[Flat],
    B12E: Float64[Flat],
    B21D: Float64[Flat],
    B21E: Float64[Flat],
    B22D: Float64[Flat],
    B22E: Float64[Flat],
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZBDSQR")
@external
def zbdsqr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NCVT: Addr(Int32),
    NRU: Addr(Int32),
    NCC: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VT: Complex128[LDVT, Flat],
    LDVT: Addr(Int32),
    U: Complex128[LDU, Flat],
    LDU: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZCGESV")
@external
def zcgesv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    WORK: Complex128[N, Flat],
    SWORK: Complex64[Flat],
    RWORK: Float64[Flat],
    ITER: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZCPOSV")
@external
def zcposv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    WORK: Complex128[N, Flat],
    SWORK: Complex64[Flat],
    RWORK: Float64[Flat],
    ITER: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZDRSCL")
@external
def zdrscl(
    N: Addr(Int32),
    SA: Addr(Float64),
    SX: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZGBBRD")
@external
def zgbbrd(
    VECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NCC: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    PT: Complex128[LDPT, Flat],
    LDPT: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBCON")
@external
def zgbcon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBEQU")
@external
def zgbequ(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBEQUB")
@external
def zgbequb(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBRFS")
@external
def zgbrfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBRFSX")
@external
def zgbrfsx(
    TRANS: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBSV")
@external
def zgbsv(
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBSVX")
@external
def zgbsvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBSVXX")
@external
def zgbsvxx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    RPVGRW: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBTF2")
@external
def zgbtf2(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBTRF")
@external
def zgbtrf(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGBTRS")
@external
def zgbtrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEBAK")
@external
def zgebak(
    JOB: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float64[Flat],
    M: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEBAL")
@external
def zgebal(
    JOB: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEBD2")
@external
def zgebd2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Complex128[Flat],
    TAUP: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEBRD")
@external
def zgebrd(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Complex128[Flat],
    TAUP: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGECON")
@external
def zgecon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Addr(Arg(11)), Addr(Arg(12)), Return('K', 0), Arg(13), Arg(14), Addr(Arg(15)), Arg(16), Arg(17), Addr(Arg(18)), Arg(19), Addr(Arg(20)), Arg(21), Addr(Arg(22)), Arg(23), Addr(Arg(24)), Arg(25), Addr(Arg(26)), Arg(27), Addr(Arg(28)), Return('INFO', 10)])
def zgedmd(
    JOBS: Addr(Const(String[1])),
    JOBZ: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBF: Addr(Const(String[1])),
    WHTSVD: Const(Int32),
    M: Const(Int32),
    N: Const(Int32),
    X: Complex128[LDX, Flat],
    LDX: Const(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Const(Int32),
    NRNK: Const(Int32),
    TOL: Const(Float64),
    EIGS: Complex128[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Const(Int32),
    RES: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Const(Int32),
    W: Complex128[LDW, Flat],
    LDW: Const(Int32),
    S: Complex128[LDS, Flat],
    LDS: Const(Int32),
    ZWORK: Complex128[Flat],
    LZWORK: Const(Int32),
    RWORK: Float64[Flat],
    LRWORK: Const(Int32),
    IWORK: Int32[Flat],
    LIWORK: Const(Int32)
) -> tuple[Int32, Returns["EIGS", Complex128[Flat]], Returns["Z", Complex128[LDZ, Flat]], Returns["RES", Float64[Flat]], Returns["B", Complex128[LDB, Flat]], Returns["W", Complex128[LDW, Flat]], Returns["S", Complex128[LDS, Flat]], Returns["ZWORK", Complex128[Flat]], Returns["RWORK", Float64[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("ZGEDMDQ")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Arg(11), Addr(Arg(12)), Arg(13), Addr(Arg(14)), Addr(Arg(15)), Addr(Arg(16)), Return('K', 2), Arg(17), Arg(18), Addr(Arg(19)), Arg(20), Arg(21), Addr(Arg(22)), Arg(23), Addr(Arg(24)), Arg(25), Addr(Arg(26)), Arg(27), Addr(Arg(28)), Arg(29), Addr(Arg(30)), Arg(31), Addr(Arg(32)), Return('INFO', 12)])
def zgedmdq(
    JOBS: Addr(Const(String[1])),
    JOBZ: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    JOBT: Addr(Const(String[1])),
    JOBF: Addr(Const(String[1])),
    WHTSVD: Const(Int32),
    M: Const(Int32),
    N: Const(Int32),
    F: Complex128[LDF, Flat],
    LDF: Const(Int32),
    X: Complex128[LDX, Flat],
    LDX: Const(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Const(Int32),
    NRNK: Const(Int32),
    TOL: Const(Float64),
    EIGS: Complex128[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Const(Int32),
    RES: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Const(Int32),
    V: Complex128[LDV, Flat],
    LDV: Const(Int32),
    S: Complex128[LDS, Flat],
    LDS: Const(Int32),
    ZWORK: Complex128[Flat],
    LZWORK: Const(Int32),
    WORK: Float64[Flat],
    LWORK: Const(Int32),
    IWORK: Int32[Flat],
    LIWORK: Const(Int32)
) -> tuple[Returns["X", Complex128[LDX, Flat]], Returns["Y", Complex128[LDY, Flat]], Int32, Returns["EIGS", Complex128[Flat]], Returns["Z", Complex128[LDZ, Flat]], Returns["RES", Float64[Flat]], Returns["B", Complex128[LDB, Flat]], Returns["V", Complex128[LDV, Flat]], Returns["S", Complex128[LDS, Flat]], Returns["ZWORK", Complex128[Flat]], Returns["WORK", Float64[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("ZGEEQU")
@external
def zgeequ(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEEQUB")
@external
def zgeequb(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEES")
@external
def zgees(
    JOBVS: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELECT: Addr(Bool),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    SDIM: Addr(Int32),
    W: Complex128[Flat],
    VS: Complex128[LDVS, Flat],
    LDVS: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEESX")
@external
def zgeesx(
    JOBVS: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELECT: Addr(Bool),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    SDIM: Addr(Int32),
    W: Complex128[Flat],
    VS: Complex128[LDVS, Flat],
    LDVS: Addr(Int32),
    RCONDE: Addr(Float64),
    RCONDV: Addr(Float64),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEEV")
@external
def zgeev(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    W: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEEVX")
@external
def zgeevx(
    BALANC: Addr(Const(String[1])),
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    W: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    SCALE: Float64[Flat],
    ABNRM: Addr(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEHD2")
@external
def zgehd2(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEHRD")
@external
def zgehrd(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEJSV")
@external
def zgejsv(
    JOBA: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBT: Addr(Const(String[1])),
    JOBP: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    SVA: Float64[N],
    U: Complex128[LDU, Flat],
    LDU: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    CWORK: Complex128[LWORK],
    LWORK: Addr(Int32),
    RWORK: Float64[LRWORK],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGELQ")
@external
def zgelq(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[Flat],
    TSIZE: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGELQ2")
@external
def zgelq2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGELQF")
@external
def zgelqf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGELQT")
@external
def zgelqt(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGELQT3")
@external
def zgelqt3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGELS")
@external
def zgels(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGELSD")
@external
def zgelsd(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    S: Float64[Flat],
    RCOND: Addr(Float64),
    RANK: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGELSS")
@external
def zgelss(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    S: Float64[Flat],
    RCOND: Addr(Float64),
    RANK: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGELST")
@external
def zgelst(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGELSY")
@external
def zgelsy(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    JPVT: Int32[Flat],
    RCOND: Addr(Float64),
    RANK: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEMLQ")
@external
def zgemlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[Flat],
    TSIZE: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEMLQT")
@external
def zgemlqt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEMQR")
@external
def zgemqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[Flat],
    TSIZE: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEMQRT")
@external
def zgemqrt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    NB: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQL2")
@external
def zgeql2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQLF")
@external
def zgeqlf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQP3")
@external
def zgeqp3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQP3RK")
@external
def zgeqp3rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    KMAX: Addr(Int32),
    ABSTOL: Addr(Float64),
    RELTOL: Addr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    K: Addr(Int32),
    MAXC2NRMK: Addr(Float64),
    RELMAXC2NRMK: Addr(Float64),
    JPIV: Int32[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQR")
@external
def zgeqr(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[Flat],
    TSIZE: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQR2")
@external
def zgeqr2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQR2P")
@external
def zgeqr2p(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQRF")
@external
def zgeqrf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQRFP")
@external
def zgeqrfp(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQRT")
@external
def zgeqrt(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQRT2")
@external
def zgeqrt2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGEQRT3")
@external
def zgeqrt3(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGERFS")
@external
def zgerfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGERFSX")
@external
def zgerfsx(
    TRANS: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGERQ2")
@external
def zgerq2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGERQF")
@external
def zgerqf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGESC2")
@external
def zgesc2(
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    RHS: Complex128[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Addr(Float64)
) -> None: ...

@bind("ZGESDD")
@external
def zgesdd(
    JOBZ: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Addr(Int32),
    VT: Complex128[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGESV")
@external
def zgesv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGESVD")
@external
def zgesvd(
    JOBU: Addr(Const(String[1])),
    JOBVT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Addr(Int32),
    VT: Complex128[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGESVDQ")
@external
def zgesvdq(
    JOBA: Addr(Const(String[1])),
    JOBP: Addr(Const(String[1])),
    JOBR: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    NUMRANK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    CWORK: Complex128[Flat],
    LCWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGESVDX")
@external
def zgesvdx(
    JOBU: Addr(Const(String[1])),
    JOBVT: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    NS: Addr(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Addr(Int32),
    VT: Complex128[LDVT, Flat],
    LDVT: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGESVJ")
@external
def zgesvj(
    JOBA: Addr(Const(String[1])),
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    SVA: Float64[N],
    MV: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    CWORK: Complex128[LWORK],
    LWORK: Addr(Int32),
    RWORK: Float64[LRWORK],
    LRWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGESVX")
@external
def zgesvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGESVXX")
@external
def zgesvxx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    RPVGRW: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGETC2")
@external
def zgetc2(
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGETF2")
@external
def zgetf2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGETRF")
@external
def zgetrf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGETRF2")
@external
def zgetrf2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGETRI")
@external
def zgetri(
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGETRS")
@external
def zgetrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGETSLS")
@external
def zgetsls(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGETSQRHRT")
@external
def zgetsqrhrt(
    M: Addr(Int32),
    N: Addr(Int32),
    MB1: Addr(Int32),
    NB1: Addr(Int32),
    NB2: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGBAK")
@external
def zggbak(
    JOB: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    M: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGBAL")
@external
def zggbal(
    JOB: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGES")
@external
def zgges(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VSL: Complex128[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Complex128[LDVSR, Flat],
    LDVSR: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGES3")
@external
def zgges3(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VSL: Complex128[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Complex128[LDVSR, Flat],
    LDVSR: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGESX")
@external
def zggesx(
    JOBVSL: Addr(Const(String[1])),
    JOBVSR: Addr(Const(String[1])),
    SORT: Addr(Const(String[1])),
    SELCTG: Addr(Bool),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    SDIM: Addr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VSL: Complex128[LDVSL, Flat],
    LDVSL: Addr(Int32),
    VSR: Complex128[LDVSR, Flat],
    LDVSR: Addr(Int32),
    RCONDE: Float64[2],
    RCONDV: Float64[2],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGEV")
@external
def zggev(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGEV3")
@external
def zggev3(
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGEVX")
@external
def zggevx(
    BALANC: Addr(Const(String[1])),
    JOBVL: Addr(Const(String[1])),
    JOBVR: Addr(Const(String[1])),
    SENSE: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    ABNRM: Addr(Float64),
    BBNRM: Addr(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGGLM")
@external
def zggglm(
    N: Addr(Int32),
    M: Addr(Int32),
    P: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    D: Complex128[Flat],
    X: Complex128[Flat],
    Y: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGHD3")
@external
def zgghd3(
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGHRD")
@external
def zgghrd(
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGLSE")
@external
def zgglse(
    M: Addr(Int32),
    N: Addr(Int32),
    P: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex128[Flat],
    D: Complex128[Flat],
    X: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGQRF")
@external
def zggqrf(
    N: Addr(Int32),
    M: Addr(Int32),
    P: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAUA: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    TAUB: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGRQF")
@external
def zggrqf(
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAUA: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    TAUB: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGSVD3")
@external
def zggsvd3(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    P: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGGSVP3")
@external
def zggsvp3(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    TOLA: Addr(Float64),
    TOLB: Addr(Float64),
    K: Addr(Int32),
    L: Addr(Int32),
    U: Complex128[LDU, Flat],
    LDU: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    IWORK: Int32[Flat],
    RWORK: Float64[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGSVJ0")
@external
def zgsvj0(
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    D: Complex128[N],
    SVA: Float64[N],
    MV: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    EPS: Addr(Float64),
    SFMIN: Addr(Float64),
    TOL: Addr(Float64),
    NSWEEP: Addr(Int32),
    WORK: Complex128[LWORK],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGSVJ1")
@external
def zgsvj1(
    JOBV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    D: Complex128[N],
    SVA: Float64[N],
    MV: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    EPS: Addr(Float64),
    SFMIN: Addr(Float64),
    TOL: Addr(Float64),
    NSWEEP: Addr(Int32),
    WORK: Complex128[LWORK],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGTCON")
@external
def zgtcon(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGTRFS")
@external
def zgtrfs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DLF: Complex128[Flat],
    DF: Complex128[Flat],
    DUF: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGTSV")
@external
def zgtsv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGTSVX")
@external
def zgtsvx(
    FACT: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DLF: Complex128[Flat],
    DF: Complex128[Flat],
    DUF: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGTTRF")
@external
def zgttrf(
    N: Addr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGTTRS")
@external
def zgttrs(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZGTTS2")
@external
def zgtts2(
    ITRANS: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("ZHB2ST_KERNELS")
@external
def zhb2st_kernels(
    UPLO: Addr(Const(String[1])),
    WANTZ: Addr(Bool),
    TTYPE: Addr(Int32),
    ST: Addr(Int32),
    ED: Addr(Int32),
    SWEEP: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    IB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    V: Complex128[Flat],
    TAU: Complex128[Flat],
    LDVT: Addr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZHBEV")
@external
def zhbev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHBEV_2STAGE")
@external
def zhbev_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHBEVD")
@external
def zhbevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHBEVD_2STAGE")
@external
def zhbevd_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHBEVX")
@external
def zhbevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHBEVX_2STAGE")
@external
def zhbevx_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHBGST")
@external
def zhbgst(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHBGV")
@external
def zhbgv(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHBGVD")
@external
def zhbgvd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHBGVX")
@external
def zhbgvx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KA: Addr(Int32),
    KB: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHBTRD")
@external
def zhbtrd(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHECON")
@external
def zhecon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHECON_3")
@external
def zhecon_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHECON_ROOK")
@external
def zhecon_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEEQUB")
@external
def zheequb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEEV")
@external
def zheev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEEV_2STAGE")
@external
def zheev_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEEVD")
@external
def zheevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEEVD_2STAGE")
@external
def zheevd_2stage(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEEVR")
@external
def zheevr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEEVR_2STAGE")
@external
def zheevr_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEEVX")
@external
def zheevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEEVX_2STAGE")
@external
def zheevx_2stage(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEGS2")
@external
def zhegs2(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEGST")
@external
def zhegst(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEGV")
@external
def zhegv(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEGV_2STAGE")
@external
def zhegv_2stage(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEGVD")
@external
def zhegvd(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHEGVX")
@external
def zhegvx(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHERFS")
@external
def zherfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHERFSX")
@external
def zherfsx(
    UPLO: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHESV")
@external
def zhesv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHESV_AA")
@external
def zhesv_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHESV_AA_2STAGE")
@external
def zhesv_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex128[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHESV_RK")
@external
def zhesv_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHESV_ROOK")
@external
def zhesv_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHESVX")
@external
def zhesvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHESVXX")
@external
def zhesvxx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    RPVGRW: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHESWAPR")
@external
def zheswapr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex128[LDA, N], ORDER_F],
    LDA: Addr(Int32),
    I1: Addr(Int32),
    I2: Addr(Int32)
) -> None: ...

@bind("ZHETD2")
@external
def zhetd2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETF2")
@external
def zhetf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETF2_RK")
@external
def zhetf2_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETF2_ROOK")
@external
def zhetf2_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRD")
@external
def zhetrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRD_2STAGE")
@external
def zhetrd_2stage(
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    HOUS2: Complex128[Flat],
    LHOUS2: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRD_HB2ST")
@external
def zhetrd_hb2st(
    STAGE1: Addr(Const(String[1])),
    VECT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    HOUS: Complex128[Flat],
    LHOUS: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRD_HE2HB")
@external
def zhetrd_he2hb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRF")
@external
def zhetrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRF_AA")
@external
def zhetrf_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRF_AA_2STAGE")
@external
def zhetrf_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex128[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRF_RK")
@external
def zhetrf_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRF_ROOK")
@external
def zhetrf_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRI")
@external
def zhetri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRI2")
@external
def zhetri2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRI2X")
@external
def zhetri2x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRI_3")
@external
def zhetri_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRI_3X")
@external
def zhetri_3x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRI_ROOK")
@external
def zhetri_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRS")
@external
def zhetrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRS2")
@external
def zhetrs2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRS_3")
@external
def zhetrs_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRS_AA")
@external
def zhetrs_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRS_AA_2STAGE")
@external
def zhetrs_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex128[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHETRS_ROOK")
@external
def zhetrs_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHFRK")
@external
def zhfrk(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    BETA: Addr(Float64),
    C: Complex128[Flat]
) -> None: ...

@bind("ZHGEQZ")
@external
def zhgeqz(
    JOB: Addr(Const(String[1])),
    COMPQ: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPCON")
@external
def zhpcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPEV")
@external
def zhpev(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPEVD")
@external
def zhpevd(
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPEVX")
@external
def zhpevx(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPGST")
@external
def zhpgst(
    ITYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPGV")
@external
def zhpgv(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPGVD")
@external
def zhpgvd(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPGVX")
@external
def zhpgvx(
    ITYPE: Addr(Int32),
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPRFS")
@external
def zhprfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPSV")
@external
def zhpsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPSVX")
@external
def zhpsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPTRD")
@external
def zhptrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPTRF")
@external
def zhptrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPTRI")
@external
def zhptri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHPTRS")
@external
def zhptrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHSEIN")
@external
def zhsein(
    SIDE: Addr(Const(String[1])),
    EIGSRC: Addr(Const(String[1])),
    INITV: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    W: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZHSEQR")
@external
def zhseqr(
    JOB: Addr(Const(String[1])),
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    W: Complex128[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLA_GBAMV")
@external
def zla_gbamv(
    TRANS: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    ALPHA: Addr(Float64),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float64),
    Y: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZLA_GBRCOND_C")
@external
def zla_gbrcond_c(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Addr(Bool),
    INFO: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GBRCOND_X")
@external
def zla_gbrcond_x(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GBRFSX_EXTENDED")
@external
def zla_gbrfsx_extended(
    PREC_TYPE: Addr(Int32),
    TRANS_TYPE: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Addr(Float64),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float64),
    DZ_UB: Addr(Float64),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLA_GBRPVGRW")
@external
def zla_gbrpvgrw(
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    NCOLS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Addr(Int32)
) -> Float64: ...

@bind("ZLA_GEAMV")
@external
def zla_geamv(
    TRANS: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float64),
    Y: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZLA_GERCOND_C")
@external
def zla_gercond_c(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Addr(Bool),
    INFO: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GERCOND_X")
@external
def zla_gercond_x(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GERFSX_EXTENDED")
@external
def zla_gerfsx_extended(
    PREC_TYPE: Addr(Int32),
    TRANS_TYPE: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Addr(Int32),
    ERRS_N: Float64[NRHS, Flat],
    ERRS_C: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Addr(Float64),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float64),
    DZ_UB: Addr(Float64),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLA_GERPVGRW")
@external
def zla_gerpvgrw(
    N: Addr(Int32),
    NCOLS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32)
) -> Float64: ...

@bind("ZLA_HEAMV")
@external
def zla_heamv(
    UPLO: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float64),
    Y: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZLA_HERCOND_C")
@external
def zla_hercond_c(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Addr(Bool),
    INFO: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_HERCOND_X")
@external
def zla_hercond_x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_HERFSX_EXTENDED")
@external
def zla_herfsx_extended(
    PREC_TYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Addr(Float64),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float64),
    DZ_UB: Addr(Float64),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLA_HERPVGRW")
@external
def zla_herpvgrw(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    INFO: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_LIN_BERR")
@external
def zla_lin_berr(
    N: Addr(Int32),
    NZ: Addr(Int32),
    NRHS: Addr(Int32),
    RES: Annotated[Complex128[N, NRHS], ORDER_F],
    AYB: Annotated[Float64[N, NRHS], ORDER_F],
    BERR: Float64[NRHS]
) -> None: ...

@bind("ZLA_PORCOND_C")
@external
def zla_porcond_c(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    C: Float64[Flat],
    CAPPLY: Addr(Bool),
    INFO: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_PORCOND_X")
@external
def zla_porcond_x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    X: Complex128[Flat],
    INFO: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_PORFSX_EXTENDED")
@external
def zla_porfsx_extended(
    PREC_TYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    COLEQU: Addr(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Addr(Float64),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float64),
    DZ_UB: Addr(Float64),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLA_PORPVGRW")
@external
def zla_porpvgrw(
    UPLO: Addr(Const(String[1])),
    NCOLS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_SYAMV")
@external
def zla_syamv(
    UPLO: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float64),
    Y: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZLA_SYRCOND_C")
@external
def zla_syrcond_c(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Addr(Bool),
    INFO: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_SYRCOND_X")
@external
def zla_syrcond_x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_SYRFSX_EXTENDED")
@external
def zla_syrfsx_extended(
    PREC_TYPE: Addr(Int32),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Addr(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Addr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Addr(Float64),
    ITHRESH: Addr(Int32),
    RTHRESH: Addr(Float64),
    DZ_UB: Addr(Float64),
    IGNORE_CWISE: Addr(Bool),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLA_SYRPVGRW")
@external
def zla_syrpvgrw(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    INFO: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_WWADDW")
@external
def zla_wwaddw(
    N: Addr(Int32),
    X: Complex128[Flat],
    Y: Complex128[Flat],
    W: Complex128[Flat]
) -> None: ...

@bind("ZLABRD")
@external
def zlabrd(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Complex128[Flat],
    TAUP: Complex128[Flat],
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Addr(Int32)
) -> None: ...

@bind("ZLACGV")
@external
def zlacgv(
    N: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZLACN2")
@external
def zlacn2(
    N: Addr(Int32),
    V: Complex128[Flat],
    X: Complex128[Flat],
    EST: Addr(Float64),
    KASE: Addr(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("ZLACON")
@external
def zlacon(
    N: Addr(Int32),
    V: Complex128[N],
    X: Complex128[N],
    EST: Addr(Float64),
    KASE: Addr(Int32)
) -> None: ...

@bind("ZLACP2")
@external
def zlacp2(
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("ZLACPY")
@external
def zlacpy(
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("ZLACRM")
@external
def zlacrm(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    RWORK: Float64[Flat]
) -> None: ...

@bind("ZLACRT")
@external
def zlacrt(
    N: Addr(Int32),
    CX: Complex128[Flat],
    INCX: Addr(Int32),
    CY: Complex128[Flat],
    INCY: Addr(Int32),
    C: Addr(Complex128),
    S: Addr(Complex128)
) -> None: ...

@bind("ZLADIV")
@external
def zladiv(
    X: Addr(Complex128),
    Y: Addr(Complex128)
) -> Complex128: ...

@bind("ZLAED0")
@external
def zlaed0(
    QSIZ: Addr(Int32),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    QSTORE: Complex128[LDQS, Flat],
    LDQS: Addr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAED7")
@external
def zlaed7(
    N: Addr(Int32),
    CUTPNT: Addr(Int32),
    QSIZ: Addr(Int32),
    TLVLS: Addr(Int32),
    CURLVL: Addr(Int32),
    CURPBM: Addr(Int32),
    D: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    RHO: Addr(Float64),
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
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAED8")
@external
def zlaed8(
    K: Addr(Int32),
    N: Addr(Int32),
    QSIZ: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    D: Float64[Flat],
    RHO: Addr(Float64),
    CUTPNT: Addr(Int32),
    Z: Float64[Flat],
    DLAMBDA: Float64[Flat],
    Q2: Complex128[LDQ2, Flat],
    LDQ2: Addr(Int32),
    W: Float64[Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAEIN")
@external
def zlaein(
    RIGHTV: Addr(Bool),
    NOINIT: Addr(Bool),
    N: Addr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    W: Addr(Complex128),
    V: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    RWORK: Float64[Flat],
    EPS3: Addr(Float64),
    SMLNUM: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAESY")
@external
def zlaesy(
    A: Addr(Complex128),
    B: Addr(Complex128),
    C: Addr(Complex128),
    RT1: Addr(Complex128),
    RT2: Addr(Complex128),
    EVSCAL: Addr(Complex128),
    CS1: Addr(Complex128),
    SN1: Addr(Complex128)
) -> None: ...

@bind("ZLAEV2")
@external
def zlaev2(
    A: Addr(Complex128),
    B: Addr(Complex128),
    C: Addr(Complex128),
    RT1: Addr(Float64),
    RT2: Addr(Float64),
    CS1: Addr(Float64),
    SN1: Addr(Complex128)
) -> None: ...

@bind("ZLAG2C")
@external
def zlag2c(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    SA: Complex64[LDSA, Flat],
    LDSA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAGS2")
@external
def zlags2(
    UPPER: Addr(Bool),
    A1: Addr(Float64),
    A2: Addr(Complex128),
    A3: Addr(Float64),
    B1: Addr(Float64),
    B2: Addr(Complex128),
    B3: Addr(Float64),
    CSU: Addr(Float64),
    SNU: Addr(Complex128),
    CSV: Addr(Float64),
    SNV: Addr(Complex128),
    CSQ: Addr(Float64),
    SNQ: Addr(Complex128)
) -> None: ...

@bind("ZLAGTM")
@external
def zlagtm(
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    ALPHA: Addr(Float64),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    BETA: Addr(Float64),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("ZLAHEF")
@external
def zlahef(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAHEF_AA")
@external
def zlahef_aa(
    UPLO: Addr(Const(String[1])),
    J1: Addr(Int32),
    M: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLAHEF_RK")
@external
def zlahef_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAHEF_ROOK")
@external
def zlahef_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAHQR")
@external
def zlahqr(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    W: Complex128[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAHR2")
@external
def zlahr2(
    N: Addr(Int32),
    K: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[NB],
    T: Annotated[Complex128[LDT, NB], ORDER_F],
    LDT: Addr(Int32),
    Y: Annotated[Complex128[LDY, NB], ORDER_F],
    LDY: Addr(Int32)
) -> None: ...

@bind("ZLAIC1")
@external
def zlaic1(
    JOB: Addr(Int32),
    J: Addr(Int32),
    X: Complex128[J],
    SEST: Addr(Float64),
    W: Complex128[J],
    GAMMA: Addr(Complex128),
    SESTPR: Addr(Float64),
    S: Addr(Complex128),
    C: Addr(Complex128)
) -> None: ...

@bind("ZLALS0")
@external
def zlals0(
    ICOMPQ: Addr(Int32),
    NL: Addr(Int32),
    NR: Addr(Int32),
    SQRE: Addr(Int32),
    NRHS: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    BX: Complex128[LDBX, Flat],
    LDBX: Addr(Int32),
    PERM: Int32[Flat],
    GIVPTR: Addr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Addr(Int32),
    POLES: Float64[LDGNUM, Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[LDGNUM, Flat],
    Z: Float64[Flat],
    K: Addr(Int32),
    C: Addr(Float64),
    S: Addr(Float64),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLALSA")
@external
def zlalsa(
    ICOMPQ: Addr(Int32),
    SMLSIZ: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    BX: Complex128[LDBX, Flat],
    LDBX: Addr(Int32),
    U: Float64[LDU, Flat],
    LDU: Addr(Int32),
    VT: Float64[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float64[LDU, Flat],
    DIFR: Float64[LDU, Flat],
    Z: Float64[LDU, Flat],
    POLES: Float64[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Addr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float64[LDU, Flat],
    C: Float64[Flat],
    S: Float64[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLALSD")
@external
def zlalsd(
    UPLO: Addr(Const(String[1])),
    SMLSIZ: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    RCOND: Addr(Float64),
    RANK: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAMSWLQ")
@external
def zlamswlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAMTSQR")
@external
def zlamtsqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLANGB")
@external
def zlangb(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANGE")
@external
def zlange(
    NORM: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANGT")
@external
def zlangt(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat]
) -> Float64: ...

@bind("ZLANHB")
@external
def zlanhb(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHE")
@external
def zlanhe(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHF")
@external
def zlanhf(
    NORM: Addr(Const(String[1])),
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    WORK: Annotated[Float64[Flat], SourceDims("0:*")]
) -> Float64: ...

@bind("ZLANHP")
@external
def zlanhp(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHS")
@external
def zlanhs(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHT")
@external
def zlanht(
    NORM: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat]
) -> Float64: ...

@bind("ZLANSB")
@external
def zlansb(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANSP")
@external
def zlansp(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANSY")
@external
def zlansy(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANTB")
@external
def zlantb(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANTP")
@external
def zlantp(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANTR")
@external
def zlantr(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLAPLL")
@external
def zlapll(
    N: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    Y: Complex128[Flat],
    INCY: Addr(Int32),
    SSMIN: Addr(Float64)
) -> None: ...

@bind("ZLAPMR")
@external
def zlapmr(
    FORWRD: Addr(Bool),
    M: Addr(Int32),
    N: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("ZLAPMT")
@external
def zlapmt(
    FORWRD: Addr(Bool),
    M: Addr(Int32),
    N: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("ZLAQGB")
@external
def zlaqgb(
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("ZLAQGE")
@external
def zlaqge(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Addr(Float64),
    COLCND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("ZLAQHB")
@external
def zlaqhb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("ZLAQHE")
@external
def zlaqhe(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("ZLAQHP")
@external
def zlaqhp(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("ZLAQP2")
@external
def zlaqp2(
    M: Addr(Int32),
    N: Addr(Int32),
    OFFSET: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLAQP2RK")
@external
def zlaqp2rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    IOFFSET: Addr(Int32),
    KMAX: Addr(Int32),
    ABSTOL: Addr(Float64),
    RELTOL: Addr(Float64),
    KP1: Addr(Int32),
    MAXC2NRM: Addr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    K: Addr(Int32),
    MAXC2NRMK: Addr(Float64),
    RELMAXC2NRMK: Addr(Float64),
    JPIV: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAQP3RK")
@external
def zlaqp3rk(
    M: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    IOFFSET: Addr(Int32),
    NB: Addr(Int32),
    ABSTOL: Addr(Float64),
    RELTOL: Addr(Float64),
    KP1: Addr(Int32),
    MAXC2NRM: Addr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    DONE: Addr(Bool),
    KB: Addr(Int32),
    MAXC2NRMK: Addr(Float64),
    RELMAXC2NRMK: Addr(Float64),
    JPIV: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Complex128[Flat],
    F: Complex128[LDF, Flat],
    LDF: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAQPS")
@external
def zlaqps(
    M: Addr(Int32),
    N: Addr(Int32),
    OFFSET: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Complex128[Flat],
    F: Complex128[LDF, Flat],
    LDF: Addr(Int32)
) -> None: ...

@bind("ZLAQR0")
@external
def zlaqr0(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    W: Complex128[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAQR1")
@external
def zlaqr1(
    N: Addr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    S1: Addr(Complex128),
    S2: Addr(Complex128),
    V: Complex128[Flat]
) -> None: ...

@bind("ZLAQR2")
@external
def zlaqr2(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NW: Addr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    NS: Addr(Int32),
    ND: Addr(Int32),
    SH: Complex128[Flat],
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    NH: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    NV: Addr(Int32),
    WV: Complex128[LDWV, Flat],
    LDWV: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32)
) -> None: ...

@bind("ZLAQR3")
@external
def zlaqr3(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NW: Addr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    NS: Addr(Int32),
    ND: Addr(Int32),
    SH: Complex128[Flat],
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    NH: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    NV: Addr(Int32),
    WV: Complex128[LDWV, Flat],
    LDWV: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32)
) -> None: ...

@bind("ZLAQR4")
@external
def zlaqr4(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    W: Complex128[Flat],
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAQR5")
@external
def zlaqr5(
    WANTT: Addr(Bool),
    WANTZ: Addr(Bool),
    KACC22: Addr(Int32),
    N: Addr(Int32),
    KTOP: Addr(Int32),
    KBOT: Addr(Int32),
    NSHFTS: Addr(Int32),
    S: Complex128[Flat],
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    ILOZ: Addr(Int32),
    IHIZ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    U: Complex128[LDU, Flat],
    LDU: Addr(Int32),
    NV: Addr(Int32),
    WV: Complex128[LDWV, Flat],
    LDWV: Addr(Int32),
    NH: Addr(Int32),
    WH: Complex128[LDWH, Flat],
    LDWH: Addr(Int32)
) -> None: ...

@bind("ZLAQSB")
@external
def zlaqsb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("ZLAQSP")
@external
def zlaqsp(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("ZLAQSY")
@external
def zlaqsy(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    EQUED: Addr(Const(String[1]))
) -> None: ...

@bind("ZLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Arg(10), Arg(11), Arg(12), Addr(Arg(13)), Arg(14), Addr(Arg(15)), Arg(16), Addr(Arg(17)), Arg(18), Addr(Arg(19)), Return('INFO', 1)])
def zlaqz0(
    WANTS: Addr(Const(String[1])),
    WANTQ: Addr(Const(String[1])),
    WANTZ: Addr(Const(String[1])),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    A: Complex128[LDA, Flat],
    LDA: Const(Int32),
    B: Complex128[LDB, Flat],
    LDB: Const(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Const(Int32),
    WORK: Complex128[Flat],
    LWORK: Const(Int32),
    RWORK: Float64[Flat],
    REC: Const(Int32)
) -> tuple[Returns["RWORK", Float64[Flat]], Int32]: ...

@bind("ZLAQZ1")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Addr(Arg(11)), Arg(12), Addr(Arg(13)), Addr(Arg(14)), Addr(Arg(15)), Arg(16), Addr(Arg(17))])
def zlaqz1(
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    K: Const(Int32),
    ISTARTM: Const(Int32),
    ISTOPM: Const(Int32),
    IHI: Const(Int32),
    A: Complex128[LDA, Flat],
    LDA: Const(Int32),
    B: Complex128[LDB, Flat],
    LDB: Const(Int32),
    NQ: Const(Int32),
    QSTART: Const(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Const(Int32),
    NZ: Const(Int32),
    ZSTART: Const(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Const(Int32)
) -> None: ...

@bind("ZLAQZ2")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10)), Arg(11), Addr(Arg(12)), Arg(13), Addr(Arg(14)), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Addr(Arg(18)), Arg(19), Addr(Arg(20)), Arg(21), Addr(Arg(22)), Arg(23), Addr(Arg(24)), Return('INFO', 2)])
def zlaqz2(
    ILSCHUR: Const(Bool),
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    NW: Const(Int32),
    A: Complex128[LDA, Flat],
    LDA: Const(Int32),
    B: Complex128[LDB, Flat],
    LDB: Const(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Const(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    QC: Complex128[LDQC, Flat],
    LDQC: Const(Int32),
    ZC: Complex128[LDZC, Flat],
    LDZC: Const(Int32),
    WORK: Complex128[Flat],
    LWORK: Const(Int32),
    RWORK: Float64[Flat],
    REC: Const(Int32)
) -> tuple[Int32, Int32, Int32]: ...

@bind("ZLAQZ3")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Arg(9), Arg(10), Addr(Arg(11)), Arg(12), Addr(Arg(13)), Arg(14), Addr(Arg(15)), Arg(16), Addr(Arg(17)), Arg(18), Addr(Arg(19)), Arg(20), Addr(Arg(21)), Arg(22), Addr(Arg(23)), Return('INFO', 0)])
def zlaqz3(
    ILSCHUR: Const(Bool),
    ILQ: Const(Bool),
    ILZ: Const(Bool),
    N: Const(Int32),
    ILO: Const(Int32),
    IHI: Const(Int32),
    NSHIFTS: Const(Int32),
    NBLOCK_DESIRED: Const(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    A: Complex128[LDA, Flat],
    LDA: Const(Int32),
    B: Complex128[LDB, Flat],
    LDB: Const(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Const(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Const(Int32),
    QC: Complex128[LDQC, Flat],
    LDQC: Const(Int32),
    ZC: Complex128[LDZC, Flat],
    LDZC: Const(Int32),
    WORK: Complex128[Flat],
    LWORK: Const(Int32)
) -> Int32: ...

@bind("ZLAR1V")
@external
def zlar1v(
    N: Addr(Int32),
    B1: Addr(Int32),
    BN: Addr(Int32),
    LAMBDA: Addr(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    LD: Float64[Flat],
    LLD: Float64[Flat],
    PIVMIN: Addr(Float64),
    GAPTOL: Addr(Float64),
    Z: Complex128[Flat],
    WANTNC: Addr(Bool),
    NEGCNT: Addr(Int32),
    ZTZ: Addr(Float64),
    MINGMA: Addr(Float64),
    R: Addr(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Addr(Float64),
    RESID: Addr(Float64),
    RQCORR: Addr(Float64),
    WORK: Float64[Flat]
) -> None: ...

@bind("ZLAR2V")
@external
def zlar2v(
    N: Addr(Int32),
    X: Complex128[Flat],
    Y: Complex128[Flat],
    Z: Complex128[Flat],
    INCX: Addr(Int32),
    C: Float64[Flat],
    S: Complex128[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("ZLARCM")
@external
def zlarcm(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    RWORK: Float64[Flat]
) -> None: ...

@bind("ZLARF")
@external
def zlarf(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Complex128[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARF1F")
@external
def zlarf1f(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Complex128[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARF1L")
@external
def zlarf1l(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Complex128[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARFB")
@external
def zlarfb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("ZLARFB_GETT")
@external
def zlarfb_gett(
    IDENT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("ZLARFG")
@external
def zlarfg(
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    TAU: Addr(Complex128)
) -> None: ...

@bind("ZLARFGP")
@external
def zlarfgp(
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    TAU: Addr(Complex128)
) -> None: ...

@bind("ZLARFT")
@external
def zlarft(
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    TAU: Complex128[Flat],
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32)
) -> None: ...

@bind("ZLARFX")
@external
def zlarfx(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    V: Complex128[Flat],
    TAU: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARFY")
@external
def zlarfy(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    V: Complex128[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARGV")
@external
def zlargv(
    N: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    Y: Complex128[Flat],
    INCY: Addr(Int32),
    C: Float64[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("ZLARNV")
@external
def zlarnv(
    IDIST: Addr(Int32),
    ISEED: Int32[4],
    N: Addr(Int32),
    X: Complex128[Flat]
) -> None: ...

@bind("ZLARRV")
@external
def zlarrv(
    N: Addr(Int32),
    VL: Addr(Float64),
    VU: Addr(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    PIVMIN: Addr(Float64),
    ISPLIT: Int32[Flat],
    M: Addr(Int32),
    DOL: Addr(Int32),
    DOU: Addr(Int32),
    MINRGP: Addr(Float64),
    RTOL1: Addr(Float64),
    RTOL2: Addr(Float64),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WGAP: Float64[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLARSCL2")
@external
def zlarscl2(
    M: Addr(Int32),
    N: Addr(Int32),
    D: Float64[Flat],
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32)
) -> None: ...

@bind("ZLARTG")
@external
def zlartg(
    f: Addr(Complex128),
    g: Addr(Complex128),
    c: Addr(Float64),
    s: Addr(Complex128),
    r: Addr(Complex128)
) -> None: ...

@bind("ZLARTV")
@external
def zlartv(
    N: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    Y: Complex128[Flat],
    INCY: Addr(Int32),
    C: Float64[Flat],
    S: Complex128[Flat],
    INCC: Addr(Int32)
) -> None: ...

@bind("ZLARZ")
@external
def zlarz(
    SIDE: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    V: Complex128[Flat],
    INCV: Addr(Int32),
    TAU: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARZB")
@external
def zlarzb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("ZLARZT")
@external
def zlarzt(
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    TAU: Complex128[Flat],
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32)
) -> None: ...

@bind("ZLASCL")
@external
def zlascl(
    TYPE: Addr(Const(String[1])),
    KL: Addr(Int32),
    KU: Addr(Int32),
    CFROM: Addr(Float64),
    CTO: Addr(Float64),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLASCL2")
@external
def zlascl2(
    M: Addr(Int32),
    N: Addr(Int32),
    D: Float64[Flat],
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32)
) -> None: ...

@bind("ZLASET")
@external
def zlaset(
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    BETA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("ZLASR")
@external
def zlasr(
    SIDE: Addr(Const(String[1])),
    PIVOT: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("ZLASSQ")
@external
def zlassq(
    n: Addr(Int32),
    x: Complex128[Flat],
    incx: Addr(Int32),
    scale: Addr(Float64),
    sumsq: Addr(Float64)
) -> None: ...

@bind("ZLASWLQ")
@external
def zlaswlq(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLASWP")
@external
def zlaswp(
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    K1: Addr(Int32),
    K2: Addr(Int32),
    IPIV: Int32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZLASYF")
@external
def zlasyf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLASYF_AA")
@external
def zlasyf_aa(
    UPLO: Addr(Const(String[1])),
    J1: Addr(Int32),
    M: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    H: Complex128[LDH, Flat],
    LDH: Addr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLASYF_RK")
@external
def zlasyf_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLASYF_ROOK")
@external
def zlasyf_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    KB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAT2C")
@external
def zlat2c(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    SA: Complex64[LDSA, Flat],
    LDSA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLATBS")
@external
def zlatbs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    X: Complex128[Flat],
    SCALE: Addr(Float64),
    CNORM: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLATDF")
@external
def zlatdf(
    IJOB: Addr(Int32),
    N: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    RHS: Complex128[Flat],
    RDSUM: Addr(Float64),
    RDSCAL: Addr(Float64),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("ZLATPS")
@external
def zlatps(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    SCALE: Addr(Float64),
    CNORM: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLATRD")
@external
def zlatrd(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Float64[Flat],
    TAU: Complex128[Flat],
    W: Complex128[LDW, Flat],
    LDW: Addr(Int32)
) -> None: ...

@bind("ZLATRS")
@external
def zlatrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    SCALE: Addr(Float64),
    CNORM: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLATRS3")
@external
def zlatrs3(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    NORMIN: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    SCALE: Float64[Flat],
    CNORM: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLATRZ")
@external
def zlatrz(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLATSQR")
@external
def zlatsqr(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAUNHR_COL_GETRFNP")
@external
def zlaunhr_col_getrfnp(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    D: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAUNHR_COL_GETRFNP2")
@external
def zlaunhr_col_getrfnp2(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    D: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAUU2")
@external
def zlauu2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZLAUUM")
@external
def zlauum(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPBCON")
@external
def zpbcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPBEQU")
@external
def zpbequ(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPBRFS")
@external
def zpbrfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPBSTF")
@external
def zpbstf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPBSV")
@external
def zpbsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPBSVX")
@external
def zpbsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPBTF2")
@external
def zpbtf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPBTRF")
@external
def zpbtrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPBTRS")
@external
def zpbtrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPFTRF")
@external
def zpftrf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPFTRI")
@external
def zpftri(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPFTRS")
@external
def zpftrs(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOCON")
@external
def zpocon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOEQU")
@external
def zpoequ(
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOEQUB")
@external
def zpoequb(
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPORFS")
@external
def zporfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPORFSX")
@external
def zporfsx(
    UPLO: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOSV")
@external
def zposv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOSVX")
@external
def zposvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOSVXX")
@external
def zposvxx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    RPVGRW: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOTF2")
@external
def zpotf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOTRF")
@external
def zpotrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOTRF2")
@external
def zpotrf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOTRI")
@external
def zpotri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPOTRS")
@external
def zpotrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPPCON")
@external
def zppcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPPEQU")
@external
def zppequ(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPPRFS")
@external
def zpprfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPPSV")
@external
def zppsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPPSVX")
@external
def zppsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPPTRF")
@external
def zpptrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPPTRI")
@external
def zpptri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPPTRS")
@external
def zpptrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPSTF2")
@external
def zpstf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    PIV: Int32[N],
    RANK: Addr(Int32),
    TOL: Addr(Float64),
    WORK: Float64[2 * N],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPSTRF")
@external
def zpstrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    PIV: Int32[N],
    RANK: Addr(Int32),
    TOL: Addr(Float64),
    WORK: Float64[2 * N],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPTCON")
@external
def zptcon(
    N: Addr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPTEQR")
@external
def zpteqr(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPTRFS")
@external
def zptrfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    DF: Float64[Flat],
    EF: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPTSV")
@external
def zptsv(
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPTSVX")
@external
def zptsvx(
    FACT: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    DF: Float64[Flat],
    EF: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPTTRF")
@external
def zpttrf(
    N: Addr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPTTRS")
@external
def zpttrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZPTTS2")
@external
def zptts2(
    IUPLO: Addr(Int32),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("ZROT")
@external
def zrot(
    N: Addr(Int32),
    CX: Complex128[Flat],
    INCX: Addr(Int32),
    CY: Complex128[Flat],
    INCY: Addr(Int32),
    C: Addr(Float64),
    S: Addr(Complex128)
) -> None: ...

@bind("ZRSCL")
@external
def zrscl(
    N: Addr(Int32),
    A: Addr(Complex128),
    X: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZSPCON")
@external
def zspcon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSPMV")
@external
def zspmv(
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

@bind("ZSPR")
@external
def zspr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    AP: Complex128[Flat]
) -> None: ...

@bind("ZSPRFS")
@external
def zsprfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSPSV")
@external
def zspsv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSPSVX")
@external
def zspsvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSPTRF")
@external
def zsptrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSPTRI")
@external
def zsptri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSPTRS")
@external
def zsptrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSTEDC")
@external
def zstedc(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSTEGR")
@external
def zstegr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    ABSTOL: Addr(Float64),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSTEIN")
@external
def zstein(
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    M: Addr(Int32),
    W: Float64[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSTEMR")
@external
def zstemr(
    JOBZ: Addr(Const(String[1])),
    RANGE: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Addr(Float64),
    VU: Addr(Float64),
    IL: Addr(Int32),
    IU: Addr(Int32),
    M: Addr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    NZC: Addr(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Addr(Bool),
    WORK: Float64[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSTEQR")
@external
def zsteqr(
    COMPZ: Addr(Const(String[1])),
    N: Addr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    WORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYCON")
@external
def zsycon(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYCON_3")
@external
def zsycon_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYCON_ROOK")
@external
def zsycon_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    ANORM: Addr(Float64),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYCONV")
@external
def zsyconv(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    E: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYCONVF")
@external
def zsyconvf(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYCONVF_ROOK")
@external
def zsyconvf_rook(
    UPLO: Addr(Const(String[1])),
    WAY: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYEQUB")
@external
def zsyequb(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    S: Float64[Flat],
    SCOND: Addr(Float64),
    AMAX: Addr(Float64),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYMV")
@external
def zsymv(
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

@bind("ZSYR")
@external
def zsyr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("ZSYRFS")
@external
def zsyrfs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYRFSX")
@external
def zsyrfsx(
    UPLO: Addr(Const(String[1])),
    EQUED: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYSV")
@external
def zsysv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYSV_AA")
@external
def zsysv_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYSV_AA_2STAGE")
@external
def zsysv_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex128[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYSV_RK")
@external
def zsysv_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYSV_ROOK")
@external
def zsysv_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYSVX")
@external
def zsysvx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYSVXX")
@external
def zsysvxx(
    FACT: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Addr(Int32),
    IPIV: Int32[Flat],
    EQUED: Addr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    RCOND: Addr(Float64),
    RPVGRW: Addr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Addr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Addr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYSWAPR")
@external
def zsyswapr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    I1: Addr(Int32),
    I2: Addr(Int32)
) -> None: ...

@bind("ZSYTF2")
@external
def zsytf2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTF2_RK")
@external
def zsytf2_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTF2_ROOK")
@external
def zsytf2_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRF")
@external
def zsytrf(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRF_AA")
@external
def zsytrf_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRF_AA_2STAGE")
@external
def zsytrf_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex128[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRF_RK")
@external
def zsytrf_rk(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRF_ROOK")
@external
def zsytrf_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRI")
@external
def zsytri(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRI2")
@external
def zsytri2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRI2X")
@external
def zsytri2x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRI_3")
@external
def zsytri_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRI_3X")
@external
def zsytri_3x(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRI_ROOK")
@external
def zsytri_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRS")
@external
def zsytrs(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRS2")
@external
def zsytrs2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRS_3")
@external
def zsytrs_3(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRS_AA")
@external
def zsytrs_aa(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRS_AA_2STAGE")
@external
def zsytrs_aa_2stage(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TB: Complex128[Flat],
    LTB: Addr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZSYTRS_ROOK")
@external
def zsytrs_rook(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTBCON")
@external
def ztbcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTBRFS")
@external
def ztbrfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTBTRS")
@external
def ztbtrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    KD: Addr(Int32),
    NRHS: Addr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTFSM")
@external
def ztfsm(
    TRANSR: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    B: Annotated[Complex128[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Addr(Int32)
) -> None: ...

@bind("ZTFTRI")
@external
def ztftri(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTFTTP")
@external
def ztfttp(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    AP: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTFTTR")
@external
def ztfttr(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    A: Annotated[Complex128[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTGEVC")
@external
def ztgevc(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    S: Complex128[LDS, Flat],
    LDS: Addr(Int32),
    P: Complex128[LDP, Flat],
    LDP: Addr(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTGEX2")
@external
def ztgex2(
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    J1: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTGEXC")
@external
def ztgexc(
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    IFST: Addr(Int32),
    ILST: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTGSEN")
@external
def ztgsen(
    IJOB: Addr(Int32),
    WANTQ: Addr(Bool),
    WANTZ: Addr(Bool),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Addr(Int32),
    M: Addr(Int32),
    PL: Addr(Float64),
    PR: Addr(Float64),
    DIF: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTGSJA")
@external
def ztgsja(
    JOBU: Addr(Const(String[1])),
    JOBV: Addr(Const(String[1])),
    JOBQ: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    TOLA: Addr(Float64),
    TOLB: Addr(Float64),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Complex128[Flat],
    NCYCLE: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTGSNA")
@external
def ztgsna(
    JOB: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    S: Float64[Flat],
    DIF: Float64[Flat],
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTGSY2")
@external
def ztgsy2(
    TRANS: Addr(Const(String[1])),
    IJOB: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    D: Complex128[LDD, Flat],
    LDD: Addr(Int32),
    E: Complex128[LDE, Flat],
    LDE: Addr(Int32),
    F: Complex128[LDF, Flat],
    LDF: Addr(Int32),
    SCALE: Addr(Float64),
    RDSUM: Addr(Float64),
    RDSCAL: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTGSYL")
@external
def ztgsyl(
    TRANS: Addr(Const(String[1])),
    IJOB: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    D: Complex128[LDD, Flat],
    LDD: Addr(Int32),
    E: Complex128[LDE, Flat],
    LDE: Addr(Int32),
    F: Complex128[LDF, Flat],
    LDF: Addr(Int32),
    SCALE: Addr(Float64),
    DIF: Addr(Float64),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPCON")
@external
def ztpcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPLQT")
@external
def ztplqt(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    MB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPLQT2")
@external
def ztplqt2(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPMLQT")
@external
def ztpmlqt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    MB: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPMQRT")
@external
def ztpmqrt(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    NB: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPQRT")
@external
def ztpqrt(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPQRT2")
@external
def ztpqrt2(
    M: Addr(Int32),
    N: Addr(Int32),
    L: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPRFB")
@external
def ztprfb(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIRECT: Addr(Const(String[1])),
    STOREV: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Addr(Int32)
) -> None: ...

@bind("ZTPRFS")
@external
def ztprfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPTRI")
@external
def ztptri(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPTRS")
@external
def ztptrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPTTF")
@external
def ztpttf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Annotated[Complex128[Flat], SourceDims("0:*")],
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTPTTR")
@external
def ztpttr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRCON")
@external
def ztrcon(
    NORM: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    RCOND: Addr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTREVC")
@external
def ztrevc(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTREVC3")
@external
def ztrevc3(
    SIDE: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTREXC")
@external
def ztrexc(
    COMPQ: Addr(Const(String[1])),
    N: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    IFST: Addr(Int32),
    ILST: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRRFS")
@external
def ztrrfs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Addr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRSEN")
@external
def ztrsen(
    JOB: Addr(Const(String[1])),
    COMPQ: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    W: Complex128[Flat],
    M: Addr(Int32),
    S: Addr(Float64),
    SEP: Addr(Float64),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRSNA")
@external
def ztrsna(
    JOB: Addr(Const(String[1])),
    HOWMNY: Addr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Addr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Addr(Int32),
    S: Float64[Flat],
    SEP: Float64[Flat],
    MM: Addr(Int32),
    M: Addr(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Addr(Int32),
    RWORK: Float64[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRSYL")
@external
def ztrsyl(
    TRANA: Addr(Const(String[1])),
    TRANB: Addr(Const(String[1])),
    ISGN: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    SCALE: Addr(Float64),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRSYL3")
@external
def ztrsyl3(
    TRANA: Addr(Const(String[1])),
    TRANB: Addr(Const(String[1])),
    ISGN: Addr(Int32),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    SCALE: Addr(Float64),
    SWORK: Float64[LDSWORK, Flat],
    LDSWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRTI2")
@external
def ztrti2(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRTRI")
@external
def ztrtri(
    UPLO: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRTRS")
@external
def ztrtrs(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    NRHS: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRTTF")
@external
def ztrttf(
    TRANSR: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Annotated[Complex128[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Addr(Int32),
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTRTTP")
@external
def ztrttp(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    AP: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZTZRZF")
@external
def ztzrzf(
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNBDB")
@external
def zunbdb(
    TRANS: Addr(Const(String[1])),
    SIGNS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Addr(Int32),
    X12: Complex128[LDX12, Flat],
    LDX12: Addr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Addr(Int32),
    X22: Complex128[LDX22, Flat],
    LDX22: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    TAUQ2: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNBDB1")
@external
def zunbdb1(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNBDB2")
@external
def zunbdb2(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNBDB3")
@external
def zunbdb3(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNBDB4")
@external
def zunbdb4(
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    PHANTOM: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNBDB5")
@external
def zunbdb5(
    M1: Addr(Int32),
    M2: Addr(Int32),
    N: Addr(Int32),
    X1: Complex128[Flat],
    INCX1: Addr(Int32),
    X2: Complex128[Flat],
    INCX2: Addr(Int32),
    Q1: Complex128[LDQ1, Flat],
    LDQ1: Addr(Int32),
    Q2: Complex128[LDQ2, Flat],
    LDQ2: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNBDB6")
@external
def zunbdb6(
    M1: Addr(Int32),
    M2: Addr(Int32),
    N: Addr(Int32),
    X1: Complex128[Flat],
    INCX1: Addr(Int32),
    X2: Complex128[Flat],
    INCX2: Addr(Int32),
    Q1: Complex128[LDQ1, Flat],
    LDQ1: Addr(Int32),
    Q2: Complex128[LDQ2, Flat],
    LDQ2: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNCSD")
@external
def zuncsd(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    JOBV2T: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    SIGNS: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Addr(Int32),
    X12: Complex128[LDX12, Flat],
    LDX12: Addr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Addr(Int32),
    X22: Complex128[LDX22, Flat],
    LDX22: Addr(Int32),
    THETA: Float64[Flat],
    U1: Complex128[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Complex128[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Complex128[LDV1T, Flat],
    LDV1T: Addr(Int32),
    V2T: Complex128[LDV2T, Flat],
    LDV2T: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNCSD2BY1")
@external
def zuncsd2by1(
    JOBU1: Addr(Const(String[1])),
    JOBU2: Addr(Const(String[1])),
    JOBV1T: Addr(Const(String[1])),
    M: Addr(Int32),
    P: Addr(Int32),
    Q: Addr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Addr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Addr(Int32),
    THETA: Float64[Flat],
    U1: Complex128[LDU1, Flat],
    LDU1: Addr(Int32),
    U2: Complex128[LDU2, Flat],
    LDU2: Addr(Int32),
    V1T: Complex128[LDV1T, Flat],
    LDV1T: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Addr(Int32),
    IWORK: Int32[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNG2L")
@external
def zung2l(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNG2R")
@external
def zung2r(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGBR")
@external
def zungbr(
    VECT: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGHR")
@external
def zunghr(
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGL2")
@external
def zungl2(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGLQ")
@external
def zunglq(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGQL")
@external
def zungql(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGQR")
@external
def zungqr(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGR2")
@external
def zungr2(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGRQ")
@external
def zungrq(
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGTR")
@external
def zungtr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGTSQR")
@external
def zungtsqr(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNGTSQR_ROW")
@external
def zungtsqr_row(
    M: Addr(Int32),
    N: Addr(Int32),
    MB: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNHR_COL")
@external
def zunhr_col(
    M: Addr(Int32),
    N: Addr(Int32),
    NB: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Addr(Int32),
    D: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNM22")
@external
def zunm22(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    N1: Addr(Int32),
    N2: Addr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNM2L")
@external
def zunm2l(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNM2R")
@external
def zunm2r(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNMBR")
@external
def zunmbr(
    VECT: Addr(Const(String[1])),
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNMHR")
@external
def zunmhr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ILO: Addr(Int32),
    IHI: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNML2")
@external
def zunml2(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNMLQ")
@external
def zunmlq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNMQL")
@external
def zunmql(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNMQR")
@external
def zunmqr(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNMR2")
@external
def zunmr2(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNMR3")
@external
def zunmr3(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNMRQ")
@external
def zunmrq(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNMRZ")
@external
def zunmrz(
    SIDE: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    L: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUNMTR")
@external
def zunmtr(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    LWORK: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUPGTR")
@external
def zupgtr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    TAU: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...

@bind("ZUPMTR")
@external
def zupmtr(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    AP: Complex128[Flat],
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32),
    WORK: Complex128[Flat],
    INFO: Addr(Int32)
) -> None: ...
