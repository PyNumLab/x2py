from . import LA_CONSTANTS
from . import LA_XISNAN

@bind("CBBCSD")
@external
def cbbcsd(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    JOBV2T: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    U1: Complex64[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Complex64[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Complex64[LDV1T, Flat],
    LDV1T: Ref(Int32),
    V2T: Complex64[LDV2T, Flat],
    LDV2T: Ref(Int32),
    B11D: Float32[Flat],
    B11E: Float32[Flat],
    B12D: Float32[Flat],
    B12E: Float32[Flat],
    B21D: Float32[Flat],
    B21E: Float32[Flat],
    B22D: Float32[Flat],
    B22E: Float32[Flat],
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CBDSQR")
@external
def cbdsqr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NCVT: Ref(Int32),
    NRU: Ref(Int32),
    NCC: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VT: Complex64[LDVT, Flat],
    LDVT: Ref(Int32),
    U: Complex64[LDU, Flat],
    LDU: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBBRD")
@external
def cgbbrd(
    VECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NCC: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    PT: Complex64[LDPT, Flat],
    LDPT: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBCON")
@external
def cgbcon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBEQU")
@external
def cgbequ(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBEQUB")
@external
def cgbequb(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBRFS")
@external
def cgbrfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBRFSX")
@external
def cgbrfsx(
    TRANS: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBSV")
@external
def cgbsv(
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBSVX")
@external
def cgbsvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBSVXX")
@external
def cgbsvxx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    RPVGRW: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBTF2")
@external
def cgbtf2(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBTRF")
@external
def cgbtrf(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGBTRS")
@external
def cgbtrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEBAK")
@external
def cgebak(
    JOB: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float32[Flat],
    M: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEBAL")
@external
def cgebal(
    JOB: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEBD2")
@external
def cgebd2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Complex64[Flat],
    TAUP: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEBRD")
@external
def cgebrd(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Complex64[Flat],
    TAUP: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGECON")
@external
def cgecon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Arg(7), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Ref(Arg(11)), Ref(Arg(12)), Return('K', 0), Arg(13), Arg(14), Ref(Arg(15)), Arg(16), Arg(17), Ref(Arg(18)), Arg(19), Ref(Arg(20)), Arg(21), Ref(Arg(22)), Arg(23), Ref(Arg(24)), Arg(25), Ref(Arg(26)), Arg(27), Ref(Arg(28)), Return('INFO', 10)])
def cgedmd(
    JOBS: Ref(Const(String[1])),
    JOBZ: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBF: Ref(Const(String[1])),
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
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Ref(Arg(6)), Ref(Arg(7)), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Arg(11), Ref(Arg(12)), Arg(13), Ref(Arg(14)), Ref(Arg(15)), Ref(Arg(16)), Return('K', 2), Arg(17), Arg(18), Ref(Arg(19)), Arg(20), Arg(21), Ref(Arg(22)), Arg(23), Ref(Arg(24)), Arg(25), Ref(Arg(26)), Arg(27), Ref(Arg(28)), Arg(29), Ref(Arg(30)), Arg(31), Ref(Arg(32)), Return('INFO', 12)])
def cgedmdq(
    JOBS: Ref(Const(String[1])),
    JOBZ: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    JOBT: Ref(Const(String[1])),
    JOBF: Ref(Const(String[1])),
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
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEEQUB")
@external
def cgeequb(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEES")
@external
def cgees(
    JOBVS: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELECT: Ref(Bool),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    SDIM: Ref(Int32),
    W: Complex64[Flat],
    VS: Complex64[LDVS, Flat],
    LDVS: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEESX")
@external
def cgeesx(
    JOBVS: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELECT: Ref(Bool),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    SDIM: Ref(Int32),
    W: Complex64[Flat],
    VS: Complex64[LDVS, Flat],
    LDVS: Ref(Int32),
    RCONDE: Ref(Float32),
    RCONDV: Ref(Float32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEEV")
@external
def cgeev(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    W: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEEVX")
@external
def cgeevx(
    BALANC: Ref(Const(String[1])),
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    W: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float32[Flat],
    ABNRM: Ref(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEHD2")
@external
def cgehd2(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEHRD")
@external
def cgehrd(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEJSV")
@external
def cgejsv(
    JOBA: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBT: Ref(Const(String[1])),
    JOBP: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    SVA: Float32[N],
    U: Complex64[LDU, Flat],
    LDU: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    CWORK: Complex64[LWORK],
    LWORK: Ref(Int32),
    RWORK: Float32[LRWORK],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGELQ")
@external
def cgelq(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[Flat],
    TSIZE: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGELQ2")
@external
def cgelq2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGELQF")
@external
def cgelqf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGELQT")
@external
def cgelqt(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGELQT3")
@external
def cgelqt3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGELS")
@external
def cgels(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGELSD")
@external
def cgelsd(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    S: Float32[Flat],
    RCOND: Ref(Float32),
    RANK: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGELSS")
@external
def cgelss(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    S: Float32[Flat],
    RCOND: Ref(Float32),
    RANK: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGELST")
@external
def cgelst(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGELSY")
@external
def cgelsy(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    JPVT: Int32[Flat],
    RCOND: Ref(Float32),
    RANK: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEMLQ")
@external
def cgemlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[Flat],
    TSIZE: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEMLQT")
@external
def cgemlqt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEMQR")
@external
def cgemqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[Flat],
    TSIZE: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEMQRT")
@external
def cgemqrt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    NB: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQL2")
@external
def cgeql2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQLF")
@external
def cgeqlf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQP3")
@external
def cgeqp3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQP3RK")
@external
def cgeqp3rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    KMAX: Ref(Int32),
    ABSTOL: Ref(Float32),
    RELTOL: Ref(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    K: Ref(Int32),
    MAXC2NRMK: Ref(Float32),
    RELMAXC2NRMK: Ref(Float32),
    JPIV: Int32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQR")
@external
def cgeqr(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[Flat],
    TSIZE: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQR2")
@external
def cgeqr2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQR2P")
@external
def cgeqr2p(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQRF")
@external
def cgeqrf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQRFP")
@external
def cgeqrfp(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQRT")
@external
def cgeqrt(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQRT2")
@external
def cgeqrt2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGEQRT3")
@external
def cgeqrt3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGERFS")
@external
def cgerfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGERFSX")
@external
def cgerfsx(
    TRANS: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGERQ2")
@external
def cgerq2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGERQF")
@external
def cgerqf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGESC2")
@external
def cgesc2(
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    RHS: Complex64[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Ref(Float32)
) -> None: ...

@bind("CGESDD")
@external
def cgesdd(
    JOBZ: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Complex64[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGESV")
@external
def cgesv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGESVD")
@external
def cgesvd(
    JOBU: Ref(Const(String[1])),
    JOBVT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Complex64[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGESVDQ")
@external
def cgesvdq(
    JOBA: Ref(Const(String[1])),
    JOBP: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    NUMRANK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    CWORK: Complex64[Flat],
    LCWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGESVDX")
@external
def cgesvdx(
    JOBU: Ref(Const(String[1])),
    JOBVT: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    NS: Ref(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Complex64[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGESVJ")
@external
def cgesvj(
    JOBA: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    SVA: Float32[N],
    MV: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    CWORK: Complex64[LWORK],
    LWORK: Ref(Int32),
    RWORK: Float32[LRWORK],
    LRWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGESVX")
@external
def cgesvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGESVXX")
@external
def cgesvxx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    RPVGRW: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGETC2")
@external
def cgetc2(
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGETF2")
@external
def cgetf2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGETRF")
@external
def cgetrf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGETRF2")
@external
def cgetrf2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGETRI")
@external
def cgetri(
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGETRS")
@external
def cgetrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGETSLS")
@external
def cgetsls(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGETSQRHRT")
@external
def cgetsqrhrt(
    M: Ref(Int32),
    N: Ref(Int32),
    MB1: Ref(Int32),
    NB1: Ref(Int32),
    NB2: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGBAK")
@external
def cggbak(
    JOB: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    M: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGBAL")
@external
def cggbal(
    JOB: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGES")
@external
def cgges(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VSL: Complex64[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Complex64[LDVSR, Flat],
    LDVSR: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGES3")
@external
def cgges3(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VSL: Complex64[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Complex64[LDVSR, Flat],
    LDVSR: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGESX")
@external
def cggesx(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VSL: Complex64[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Complex64[LDVSR, Flat],
    LDVSR: Ref(Int32),
    RCONDE: Float32[2],
    RCONDV: Float32[2],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGEV")
@external
def cggev(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGEV3")
@external
def cggev3(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGEVX")
@external
def cggevx(
    BALANC: Ref(Const(String[1])),
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    ABNRM: Ref(Float32),
    BBNRM: Ref(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGGLM")
@external
def cggglm(
    N: Ref(Int32),
    M: Ref(Int32),
    P: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    D: Complex64[Flat],
    X: Complex64[Flat],
    Y: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGHD3")
@external
def cgghd3(
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGHRD")
@external
def cgghrd(
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGLSE")
@external
def cgglse(
    M: Ref(Int32),
    N: Ref(Int32),
    P: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex64[Flat],
    D: Complex64[Flat],
    X: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGQRF")
@external
def cggqrf(
    N: Ref(Int32),
    M: Ref(Int32),
    P: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAUA: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    TAUB: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGRQF")
@external
def cggrqf(
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAUA: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    TAUB: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGSVD3")
@external
def cggsvd3(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    P: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGGSVP3")
@external
def cggsvp3(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    TOLA: Ref(Float32),
    TOLB: Ref(Float32),
    K: Ref(Int32),
    L: Ref(Int32),
    U: Complex64[LDU, Flat],
    LDU: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    IWORK: Int32[Flat],
    RWORK: Float32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGSVJ0")
@external
def cgsvj0(
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    D: Complex64[N],
    SVA: Float32[N],
    MV: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    EPS: Ref(Float32),
    SFMIN: Ref(Float32),
    TOL: Ref(Float32),
    NSWEEP: Ref(Int32),
    WORK: Complex64[LWORK],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGSVJ1")
@external
def cgsvj1(
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    D: Complex64[N],
    SVA: Float32[N],
    MV: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    EPS: Ref(Float32),
    SFMIN: Ref(Float32),
    TOL: Ref(Float32),
    NSWEEP: Ref(Int32),
    WORK: Complex64[LWORK],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGTCON")
@external
def cgtcon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGTRFS")
@external
def cgtrfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DLF: Complex64[Flat],
    DF: Complex64[Flat],
    DUF: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGTSV")
@external
def cgtsv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGTSVX")
@external
def cgtsvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DLF: Complex64[Flat],
    DF: Complex64[Flat],
    DUF: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGTTRF")
@external
def cgttrf(
    N: Ref(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CGTTRS")
@external
def cgttrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CGTTS2")
@external
def cgtts2(
    ITRANS: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("CHB2ST_KERNELS")
@external
def chb2st_kernels(
    UPLO: Ref(Const(String[1])),
    WANTZ: Ref(Bool),
    TTYPE: Ref(Int32),
    ST: Ref(Int32),
    ED: Ref(Int32),
    SWEEP: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    IB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    V: Complex64[Flat],
    TAU: Complex64[Flat],
    LDVT: Ref(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CHBEV")
@external
def chbev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHBEV_2STAGE")
@external
def chbev_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHBEVD")
@external
def chbevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHBEVD_2STAGE")
@external
def chbevd_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHBEVX")
@external
def chbevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHBEVX_2STAGE")
@external
def chbevx_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHBGST")
@external
def chbgst(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHBGV")
@external
def chbgv(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHBGVD")
@external
def chbgvd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHBGVX")
@external
def chbgvx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHBTRD")
@external
def chbtrd(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHECON")
@external
def checon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHECON_3")
@external
def checon_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHECON_ROOK")
@external
def checon_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEEQUB")
@external
def cheequb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEEV")
@external
def cheev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEEV_2STAGE")
@external
def cheev_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEEVD")
@external
def cheevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEEVD_2STAGE")
@external
def cheevd_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEEVR")
@external
def cheevr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEEVR_2STAGE")
@external
def cheevr_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEEVX")
@external
def cheevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEEVX_2STAGE")
@external
def cheevx_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEGS2")
@external
def chegs2(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEGST")
@external
def chegst(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEGV")
@external
def chegv(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEGV_2STAGE")
@external
def chegv_2stage(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEGVD")
@external
def chegvd(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHEGVX")
@external
def chegvx(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHERFS")
@external
def cherfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHERFSX")
@external
def cherfsx(
    UPLO: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHESV")
@external
def chesv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHESV_AA")
@external
def chesv_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHESV_AA_2STAGE")
@external
def chesv_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex64[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHESV_RK")
@external
def chesv_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHESV_ROOK")
@external
def chesv_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHESVX")
@external
def chesvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHESVXX")
@external
def chesvxx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    RPVGRW: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHESWAPR")
@external
def cheswapr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex64[LDA, N], ORDER_F],
    LDA: Ref(Int32),
    I1: Ref(Int32),
    I2: Ref(Int32)
) -> None: ...

@bind("CHETD2")
@external
def chetd2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETF2")
@external
def chetf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETF2_RK")
@external
def chetf2_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETF2_ROOK")
@external
def chetf2_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRD")
@external
def chetrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRD_2STAGE")
@external
def chetrd_2stage(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    HOUS2: Complex64[Flat],
    LHOUS2: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRD_HB2ST")
@external
def chetrd_hb2st(
    STAGE1: Ref(Const(String[1])),
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    HOUS: Complex64[Flat],
    LHOUS: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRD_HE2HB")
@external
def chetrd_he2hb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRF")
@external
def chetrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRF_AA")
@external
def chetrf_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRF_AA_2STAGE")
@external
def chetrf_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex64[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRF_RK")
@external
def chetrf_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRF_ROOK")
@external
def chetrf_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRI")
@external
def chetri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRI2")
@external
def chetri2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRI2X")
@external
def chetri2x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRI_3")
@external
def chetri_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRI_3X")
@external
def chetri_3x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRI_ROOK")
@external
def chetri_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRS")
@external
def chetrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRS2")
@external
def chetrs2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRS_3")
@external
def chetrs_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRS_AA")
@external
def chetrs_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRS_AA_2STAGE")
@external
def chetrs_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex64[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHETRS_ROOK")
@external
def chetrs_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHFRK")
@external
def chfrk(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    BETA: Ref(Float32),
    C: Complex64[Flat]
) -> None: ...

@bind("CHGEQZ")
@external
def chgeqz(
    JOB: Ref(Const(String[1])),
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHLA_TRANSTYPE")
@external
def chla_transtype(
    TRANS: Ref(Int32)
) -> String[1]: ...

@bind("CHPCON")
@external
def chpcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPEV")
@external
def chpev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPEVD")
@external
def chpevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPEVX")
@external
def chpevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPGST")
@external
def chpgst(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPGV")
@external
def chpgv(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPGVD")
@external
def chpgvd(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPGVX")
@external
def chpgvx(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPRFS")
@external
def chprfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPSV")
@external
def chpsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPSVX")
@external
def chpsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPTRD")
@external
def chptrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPTRF")
@external
def chptrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPTRI")
@external
def chptri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHPTRS")
@external
def chptrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CHSEIN")
@external
def chsein(
    SIDE: Ref(Const(String[1])),
    EIGSRC: Ref(Const(String[1])),
    INITV: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    W: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CHSEQR")
@external
def chseqr(
    JOB: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    W: Complex64[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLA_GBAMV")
@external
def cla_gbamv(
    TRANS: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    ALPHA: Ref(Float32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float32),
    Y: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CLA_GBRCOND_C")
@external
def cla_gbrcond_c(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Ref(Bool),
    INFO: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GBRCOND_X")
@external
def cla_gbrcond_x(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GBRFSX_EXTENDED")
@external
def cla_gbrfsx_extended(
    PREC_TYPE: Ref(Int32),
    TRANS_TYPE: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Ref(Float32),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float32),
    DZ_UB: Ref(Float32),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLA_GBRPVGRW")
@external
def cla_gbrpvgrw(
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NCOLS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ref(Int32)
) -> Float32: ...

@bind("CLA_GEAMV")
@external
def cla_geamv(
    TRANS: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float32),
    Y: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CLA_GERCOND_C")
@external
def cla_gercond_c(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Ref(Bool),
    INFO: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GERCOND_X")
@external
def cla_gercond_x(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GERFSX_EXTENDED")
@external
def cla_gerfsx_extended(
    PREC_TYPE: Ref(Int32),
    TRANS_TYPE: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ref(Int32),
    ERRS_N: Float32[NRHS, Flat],
    ERRS_C: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Ref(Float32),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float32),
    DZ_UB: Ref(Float32),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLA_GERPVGRW")
@external
def cla_gerpvgrw(
    N: Ref(Int32),
    NCOLS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32)
) -> Float32: ...

@bind("CLA_HEAMV")
@external
def cla_heamv(
    UPLO: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float32),
    Y: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CLA_HERCOND_C")
@external
def cla_hercond_c(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Ref(Bool),
    INFO: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_HERCOND_X")
@external
def cla_hercond_x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_HERFSX_EXTENDED")
@external
def cla_herfsx_extended(
    PREC_TYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Ref(Float32),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float32),
    DZ_UB: Ref(Float32),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLA_HERPVGRW")
@external
def cla_herpvgrw(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    INFO: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_LIN_BERR")
@external
def cla_lin_berr(
    N: Ref(Int32),
    NZ: Ref(Int32),
    NRHS: Ref(Int32),
    RES: Annotated[Complex64[N, NRHS], ORDER_F],
    AYB: Annotated[Float32[N, NRHS], ORDER_F],
    BERR: Float32[NRHS]
) -> None: ...

@bind("CLA_PORCOND_C")
@external
def cla_porcond_c(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    C: Float32[Flat],
    CAPPLY: Ref(Bool),
    INFO: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_PORCOND_X")
@external
def cla_porcond_x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    X: Complex64[Flat],
    INFO: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_PORFSX_EXTENDED")
@external
def cla_porfsx_extended(
    PREC_TYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    COLEQU: Ref(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Ref(Float32),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float32),
    DZ_UB: Ref(Float32),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLA_PORPVGRW")
@external
def cla_porpvgrw(
    UPLO: Ref(Const(String[1])),
    NCOLS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_SYAMV")
@external
def cla_syamv(
    UPLO: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float32),
    Y: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CLA_SYRCOND_C")
@external
def cla_syrcond_c(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Ref(Bool),
    INFO: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_SYRCOND_X")
@external
def cla_syrcond_x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_SYRFSX_EXTENDED")
@external
def cla_syrfsx_extended(
    PREC_TYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Ref(Float32),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float32),
    DZ_UB: Ref(Float32),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLA_SYRPVGRW")
@external
def cla_syrpvgrw(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    INFO: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_WWADDW")
@external
def cla_wwaddw(
    N: Ref(Int32),
    X: Complex64[Flat],
    Y: Complex64[Flat],
    W: Complex64[Flat]
) -> None: ...

@bind("CLABRD")
@external
def clabrd(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Complex64[Flat],
    TAUP: Complex64[Flat],
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ref(Int32)
) -> None: ...

@bind("CLACGV")
@external
def clacgv(
    N: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CLACN2")
@external
def clacn2(
    N: Ref(Int32),
    V: Complex64[Flat],
    X: Complex64[Flat],
    EST: Ref(Float32),
    KASE: Ref(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("CLACON")
@external
def clacon(
    N: Ref(Int32),
    V: Complex64[N],
    X: Complex64[N],
    EST: Ref(Float32),
    KASE: Ref(Int32)
) -> None: ...

@bind("CLACP2")
@external
def clacp2(
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("CLACPY")
@external
def clacpy(
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("CLACRM")
@external
def clacrm(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    RWORK: Float32[Flat]
) -> None: ...

@bind("CLACRT")
@external
def clacrt(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32),
    CY: Complex64[Flat],
    INCY: Ref(Int32),
    C: Ref(Complex64),
    S: Ref(Complex64)
) -> None: ...

@bind("CLADIV")
@external
def cladiv(
    X: Ref(Complex64),
    Y: Ref(Complex64)
) -> Complex64: ...

@bind("CLAED0")
@external
def claed0(
    QSIZ: Ref(Int32),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    QSTORE: Complex64[LDQS, Flat],
    LDQS: Ref(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAED7")
@external
def claed7(
    N: Ref(Int32),
    CUTPNT: Ref(Int32),
    QSIZ: Ref(Int32),
    TLVLS: Ref(Int32),
    CURLVL: Ref(Int32),
    CURPBM: Ref(Int32),
    D: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    RHO: Ref(Float32),
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
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAED8")
@external
def claed8(
    K: Ref(Int32),
    N: Ref(Int32),
    QSIZ: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    D: Float32[Flat],
    RHO: Ref(Float32),
    CUTPNT: Ref(Int32),
    Z: Float32[Flat],
    DLAMBDA: Float32[Flat],
    Q2: Complex64[LDQ2, Flat],
    LDQ2: Ref(Int32),
    W: Float32[Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAEIN")
@external
def claein(
    RIGHTV: Ref(Bool),
    NOINIT: Ref(Bool),
    N: Ref(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    W: Ref(Complex64),
    V: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    RWORK: Float32[Flat],
    EPS3: Ref(Float32),
    SMLNUM: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAESY")
@external
def claesy(
    A: Ref(Complex64),
    B: Ref(Complex64),
    C: Ref(Complex64),
    RT1: Ref(Complex64),
    RT2: Ref(Complex64),
    EVSCAL: Ref(Complex64),
    CS1: Ref(Complex64),
    SN1: Ref(Complex64)
) -> None: ...

@bind("CLAEV2")
@external
def claev2(
    A: Ref(Complex64),
    B: Ref(Complex64),
    C: Ref(Complex64),
    RT1: Ref(Float32),
    RT2: Ref(Float32),
    CS1: Ref(Float32),
    SN1: Ref(Complex64)
) -> None: ...

@bind("CLAG2Z")
@external
def clag2z(
    M: Ref(Int32),
    N: Ref(Int32),
    SA: Complex64[LDSA, Flat],
    LDSA: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAGS2")
@external
def clags2(
    UPPER: Ref(Bool),
    A1: Ref(Float32),
    A2: Ref(Complex64),
    A3: Ref(Float32),
    B1: Ref(Float32),
    B2: Ref(Complex64),
    B3: Ref(Float32),
    CSU: Ref(Float32),
    SNU: Ref(Complex64),
    CSV: Ref(Float32),
    SNV: Ref(Complex64),
    CSQ: Ref(Float32),
    SNQ: Ref(Complex64)
) -> None: ...

@bind("CLAGTM")
@external
def clagtm(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    ALPHA: Ref(Float32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    BETA: Ref(Float32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("CLAHEF")
@external
def clahef(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAHEF_AA")
@external
def clahef_aa(
    UPLO: Ref(Const(String[1])),
    J1: Ref(Int32),
    M: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLAHEF_RK")
@external
def clahef_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAHEF_ROOK")
@external
def clahef_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAHQR")
@external
def clahqr(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    W: Complex64[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAHR2")
@external
def clahr2(
    N: Ref(Int32),
    K: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[NB],
    T: Annotated[Complex64[LDT, NB], ORDER_F],
    LDT: Ref(Int32),
    Y: Annotated[Complex64[LDY, NB], ORDER_F],
    LDY: Ref(Int32)
) -> None: ...

@bind("CLAIC1")
@external
def claic1(
    JOB: Ref(Int32),
    J: Ref(Int32),
    X: Complex64[J],
    SEST: Ref(Float32),
    W: Complex64[J],
    GAMMA: Ref(Complex64),
    SESTPR: Ref(Float32),
    S: Ref(Complex64),
    C: Ref(Complex64)
) -> None: ...

@bind("CLALS0")
@external
def clals0(
    ICOMPQ: Ref(Int32),
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    NRHS: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    BX: Complex64[LDBX, Flat],
    LDBX: Ref(Int32),
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Ref(Int32),
    POLES: Float32[LDGNUM, Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[LDGNUM, Flat],
    Z: Float32[Flat],
    K: Ref(Int32),
    C: Ref(Float32),
    S: Ref(Float32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLALSA")
@external
def clalsa(
    ICOMPQ: Ref(Int32),
    SMLSIZ: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    BX: Complex64[LDBX, Flat],
    LDBX: Ref(Int32),
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float32[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float32[LDU, Flat],
    DIFR: Float32[LDU, Flat],
    Z: Float32[LDU, Flat],
    POLES: Float32[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float32[LDU, Flat],
    C: Float32[Flat],
    S: Float32[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLALSD")
@external
def clalsd(
    UPLO: Ref(Const(String[1])),
    SMLSIZ: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    RCOND: Ref(Float32),
    RANK: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAMSWLQ")
@external
def clamswlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAMTSQR")
@external
def clamtsqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLANGB")
@external
def clangb(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANGE")
@external
def clange(
    NORM: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANGT")
@external
def clangt(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat]
) -> Float32: ...

@bind("CLANHB")
@external
def clanhb(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHE")
@external
def clanhe(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHF")
@external
def clanhf(
    NORM: Ref(Const(String[1])),
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    WORK: Annotated[Float32[Flat], SourceDims("0:*")]
) -> Float32: ...

@bind("CLANHP")
@external
def clanhp(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHS")
@external
def clanhs(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHT")
@external
def clanht(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Complex64[Flat]
) -> Float32: ...

@bind("CLANSB")
@external
def clansb(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANSP")
@external
def clansp(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANSY")
@external
def clansy(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANTB")
@external
def clantb(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANTP")
@external
def clantp(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANTR")
@external
def clantr(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLAPLL")
@external
def clapll(
    N: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    Y: Complex64[Flat],
    INCY: Ref(Int32),
    SSMIN: Ref(Float32)
) -> None: ...

@bind("CLAPMR")
@external
def clapmr(
    FORWRD: Ref(Bool),
    M: Ref(Int32),
    N: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("CLAPMT")
@external
def clapmt(
    FORWRD: Ref(Bool),
    M: Ref(Int32),
    N: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("CLAQGB")
@external
def claqgb(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("CLAQGE")
@external
def claqge(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("CLAQHB")
@external
def claqhb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("CLAQHE")
@external
def claqhe(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("CLAQHP")
@external
def claqhp(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("CLAQP2")
@external
def claqp2(
    M: Ref(Int32),
    N: Ref(Int32),
    OFFSET: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLAQP2RK")
@external
def claqp2rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    IOFFSET: Ref(Int32),
    KMAX: Ref(Int32),
    ABSTOL: Ref(Float32),
    RELTOL: Ref(Float32),
    KP1: Ref(Int32),
    MAXC2NRM: Ref(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    K: Ref(Int32),
    MAXC2NRMK: Ref(Float32),
    RELMAXC2NRMK: Ref(Float32),
    JPIV: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAQP3RK")
@external
def claqp3rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    IOFFSET: Ref(Int32),
    NB: Ref(Int32),
    ABSTOL: Ref(Float32),
    RELTOL: Ref(Float32),
    KP1: Ref(Int32),
    MAXC2NRM: Ref(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    DONE: Ref(Bool),
    KB: Ref(Int32),
    MAXC2NRMK: Ref(Float32),
    RELMAXC2NRMK: Ref(Float32),
    JPIV: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Complex64[Flat],
    F: Complex64[LDF, Flat],
    LDF: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAQPS")
@external
def claqps(
    M: Ref(Int32),
    N: Ref(Int32),
    OFFSET: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Complex64[Flat],
    F: Complex64[LDF, Flat],
    LDF: Ref(Int32)
) -> None: ...

@bind("CLAQR0")
@external
def claqr0(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    W: Complex64[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAQR1")
@external
def claqr1(
    N: Ref(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    S1: Ref(Complex64),
    S2: Ref(Complex64),
    V: Complex64[Flat]
) -> None: ...

@bind("CLAQR2")
@external
def claqr2(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NW: Ref(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    NS: Ref(Int32),
    ND: Ref(Int32),
    SH: Complex64[Flat],
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    NH: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    NV: Ref(Int32),
    WV: Complex64[LDWV, Flat],
    LDWV: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32)
) -> None: ...

@bind("CLAQR3")
@external
def claqr3(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NW: Ref(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    NS: Ref(Int32),
    ND: Ref(Int32),
    SH: Complex64[Flat],
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    NH: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    NV: Ref(Int32),
    WV: Complex64[LDWV, Flat],
    LDWV: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32)
) -> None: ...

@bind("CLAQR4")
@external
def claqr4(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    W: Complex64[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAQR5")
@external
def claqr5(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    KACC22: Ref(Int32),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NSHFTS: Ref(Int32),
    S: Complex64[Flat],
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    U: Complex64[LDU, Flat],
    LDU: Ref(Int32),
    NV: Ref(Int32),
    WV: Complex64[LDWV, Flat],
    LDWV: Ref(Int32),
    NH: Ref(Int32),
    WH: Complex64[LDWH, Flat],
    LDWH: Ref(Int32)
) -> None: ...

@bind("CLAQSB")
@external
def claqsb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("CLAQSP")
@external
def claqsp(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("CLAQSY")
@external
def claqsy(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("CLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Arg(6), Ref(Arg(7)), Arg(8), Ref(Arg(9)), Arg(10), Arg(11), Arg(12), Ref(Arg(13)), Arg(14), Ref(Arg(15)), Arg(16), Ref(Arg(17)), Arg(18), Ref(Arg(19)), Return('INFO', 1)])
def claqz0(
    WANTS: Ref(Const(String[1])),
    WANTQ: Ref(Const(String[1])),
    WANTZ: Ref(Const(String[1])),
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Arg(6), Ref(Arg(7)), Arg(8), Ref(Arg(9)), Ref(Arg(10)), Ref(Arg(11)), Arg(12), Ref(Arg(13)), Ref(Arg(14)), Ref(Arg(15)), Arg(16), Ref(Arg(17))])
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Arg(7), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Arg(11), Ref(Arg(12)), Arg(13), Ref(Arg(14)), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Ref(Arg(18)), Arg(19), Ref(Arg(20)), Arg(21), Ref(Arg(22)), Arg(23), Ref(Arg(24)), Return('INFO', 2)])
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Ref(Arg(7)), Arg(8), Arg(9), Arg(10), Ref(Arg(11)), Arg(12), Ref(Arg(13)), Arg(14), Ref(Arg(15)), Arg(16), Ref(Arg(17)), Arg(18), Ref(Arg(19)), Arg(20), Ref(Arg(21)), Arg(22), Ref(Arg(23)), Return('INFO', 0)])
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
    N: Ref(Int32),
    B1: Ref(Int32),
    BN: Ref(Int32),
    LAMBDA: Ref(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    LD: Float32[Flat],
    LLD: Float32[Flat],
    PIVMIN: Ref(Float32),
    GAPTOL: Ref(Float32),
    Z: Complex64[Flat],
    WANTNC: Ref(Bool),
    NEGCNT: Ref(Int32),
    ZTZ: Ref(Float32),
    MINGMA: Ref(Float32),
    R: Ref(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Ref(Float32),
    RESID: Ref(Float32),
    RQCORR: Ref(Float32),
    WORK: Float32[Flat]
) -> None: ...

@bind("CLAR2V")
@external
def clar2v(
    N: Ref(Int32),
    X: Complex64[Flat],
    Y: Complex64[Flat],
    Z: Complex64[Flat],
    INCX: Ref(Int32),
    C: Float32[Flat],
    S: Complex64[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("CLARCM")
@external
def clarcm(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    RWORK: Float32[Flat]
) -> None: ...

@bind("CLARF")
@external
def clarf(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Complex64[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARF1F")
@external
def clarf1f(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Complex64[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARF1L")
@external
def clarf1l(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Complex64[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARFB")
@external
def clarfb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("CLARFB_GETT")
@external
def clarfb_gett(
    IDENT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("CLARFG")
@external
def clarfg(
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    TAU: Ref(Complex64)
) -> None: ...

@bind("CLARFGP")
@external
def clarfgp(
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    TAU: Ref(Complex64)
) -> None: ...

@bind("CLARFT")
@external
def clarft(
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    TAU: Complex64[Flat],
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32)
) -> None: ...

@bind("CLARFX")
@external
def clarfx(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Complex64[Flat],
    TAU: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARFY")
@external
def clarfy(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    V: Complex64[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARGV")
@external
def clargv(
    N: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    Y: Complex64[Flat],
    INCY: Ref(Int32),
    C: Float32[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("CLARNV")
@external
def clarnv(
    IDIST: Ref(Int32),
    ISEED: Int32[4],
    N: Ref(Int32),
    X: Complex64[Flat]
) -> None: ...

@bind("CLARRV")
@external
def clarrv(
    N: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    PIVMIN: Ref(Float32),
    ISPLIT: Int32[Flat],
    M: Ref(Int32),
    DOL: Ref(Int32),
    DOU: Ref(Int32),
    MINRGP: Ref(Float32),
    RTOL1: Ref(Float32),
    RTOL2: Ref(Float32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WGAP: Float32[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLARSCL2")
@external
def clarscl2(
    M: Ref(Int32),
    N: Ref(Int32),
    D: Float32[Flat],
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32)
) -> None: ...

@bind("CLARTG")
@external
def clartg(
    f: Ref(Complex64),
    g: Ref(Complex64),
    c: Ref(Float32),
    s: Ref(Complex64),
    r: Ref(Complex64)
) -> None: ...

@bind("CLARTV")
@external
def clartv(
    N: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    Y: Complex64[Flat],
    INCY: Ref(Int32),
    C: Float32[Flat],
    S: Complex64[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("CLARZ")
@external
def clarz(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    V: Complex64[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARZB")
@external
def clarzb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("CLARZT")
@external
def clarzt(
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    TAU: Complex64[Flat],
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32)
) -> None: ...

@bind("CLASCL")
@external
def clascl(
    TYPE: Ref(Const(String[1])),
    KL: Ref(Int32),
    KU: Ref(Int32),
    CFROM: Ref(Float32),
    CTO: Ref(Float32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLASCL2")
@external
def clascl2(
    M: Ref(Int32),
    N: Ref(Int32),
    D: Float32[Flat],
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32)
) -> None: ...

@bind("CLASET")
@external
def claset(
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    BETA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("CLASR")
@external
def clasr(
    SIDE: Ref(Const(String[1])),
    PIVOT: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("CLASSQ")
@external
def classq(
    n: Ref(Int32),
    x: Complex64[Flat],
    incx: Ref(Int32),
    scale: Ref(Float32),
    sumsq: Ref(Float32)
) -> None: ...

@bind("CLASWLQ")
@external
def claswlq(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLASWP")
@external
def claswp(
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    K1: Ref(Int32),
    K2: Ref(Int32),
    IPIV: Int32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CLASYF")
@external
def clasyf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLASYF_AA")
@external
def clasyf_aa(
    UPLO: Ref(Const(String[1])),
    J1: Ref(Int32),
    M: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    H: Complex64[LDH, Flat],
    LDH: Ref(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLASYF_RK")
@external
def clasyf_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLASYF_ROOK")
@external
def clasyf_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLATBS")
@external
def clatbs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    X: Complex64[Flat],
    SCALE: Ref(Float32),
    CNORM: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLATDF")
@external
def clatdf(
    IJOB: Ref(Int32),
    N: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    RHS: Complex64[Flat],
    RDSUM: Ref(Float32),
    RDSCAL: Ref(Float32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("CLATPS")
@external
def clatps(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    SCALE: Ref(Float32),
    CNORM: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLATRD")
@external
def clatrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    TAU: Complex64[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ref(Int32)
) -> None: ...

@bind("CLATRS")
@external
def clatrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    SCALE: Ref(Float32),
    CNORM: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLATRS3")
@external
def clatrs3(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    SCALE: Float32[Flat],
    CNORM: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLATRZ")
@external
def clatrz(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLATSQR")
@external
def clatsqr(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAUNHR_COL_GETRFNP")
@external
def claunhr_col_getrfnp(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    D: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAUNHR_COL_GETRFNP2")
@external
def claunhr_col_getrfnp2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    D: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAUU2")
@external
def clauu2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CLAUUM")
@external
def clauum(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPBCON")
@external
def cpbcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPBEQU")
@external
def cpbequ(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPBRFS")
@external
def cpbrfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPBSTF")
@external
def cpbstf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPBSV")
@external
def cpbsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPBSVX")
@external
def cpbsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPBTF2")
@external
def cpbtf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPBTRF")
@external
def cpbtrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPBTRS")
@external
def cpbtrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPFTRF")
@external
def cpftrf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPFTRI")
@external
def cpftri(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPFTRS")
@external
def cpftrs(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOCON")
@external
def cpocon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOEQU")
@external
def cpoequ(
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOEQUB")
@external
def cpoequb(
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPORFS")
@external
def cporfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPORFSX")
@external
def cporfsx(
    UPLO: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOSV")
@external
def cposv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOSVX")
@external
def cposvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOSVXX")
@external
def cposvxx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    RPVGRW: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOTF2")
@external
def cpotf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOTRF")
@external
def cpotrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOTRF2")
@external
def cpotrf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOTRI")
@external
def cpotri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPOTRS")
@external
def cpotrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPPCON")
@external
def cppcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPPEQU")
@external
def cppequ(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPPRFS")
@external
def cpprfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPPSV")
@external
def cppsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPPSVX")
@external
def cppsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPPTRF")
@external
def cpptrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPPTRI")
@external
def cpptri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPPTRS")
@external
def cpptrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPSTF2")
@external
def cpstf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    PIV: Int32[N],
    RANK: Ref(Int32),
    TOL: Ref(Float32),
    WORK: Float32[2 * N],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPSTRF")
@external
def cpstrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    PIV: Int32[N],
    RANK: Ref(Int32),
    TOL: Ref(Float32),
    WORK: Float32[2 * N],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPTCON")
@external
def cptcon(
    N: Ref(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPTEQR")
@external
def cpteqr(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPTRFS")
@external
def cptrfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    DF: Float32[Flat],
    EF: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPTSV")
@external
def cptsv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPTSVX")
@external
def cptsvx(
    FACT: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    DF: Float32[Flat],
    EF: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPTTRF")
@external
def cpttrf(
    N: Ref(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CPTTRS")
@external
def cpttrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CPTTS2")
@external
def cptts2(
    IUPLO: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("CROT")
@external
def crot(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32),
    CY: Complex64[Flat],
    INCY: Ref(Int32),
    C: Ref(Float32),
    S: Ref(Complex64)
) -> None: ...

@bind("CRSCL")
@external
def crscl(
    N: Ref(Int32),
    A: Ref(Complex64),
    X: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CSPCON")
@external
def cspcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSPMV")
@external
def cspmv(
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

@bind("CSPR")
@external
def cspr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    AP: Complex64[Flat]
) -> None: ...

@bind("CSPRFS")
@external
def csprfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSPSV")
@external
def cspsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSPSVX")
@external
def cspsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSPTRF")
@external
def csptrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSPTRI")
@external
def csptri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSPTRS")
@external
def csptrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSRSCL")
@external
def csrscl(
    N: Ref(Int32),
    SA: Ref(Float32),
    SX: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CSTEDC")
@external
def cstedc(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSTEGR")
@external
def cstegr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSTEIN")
@external
def cstein(
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    M: Ref(Int32),
    W: Float32[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSTEMR")
@external
def cstemr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    NZC: Ref(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Ref(Bool),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSTEQR")
@external
def csteqr(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYCON")
@external
def csycon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYCON_3")
@external
def csycon_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYCON_ROOK")
@external
def csycon_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYCONV")
@external
def csyconv(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    E: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYCONVF")
@external
def csyconvf(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYCONVF_ROOK")
@external
def csyconvf_rook(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYEQUB")
@external
def csyequb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYMV")
@external
def csymv(
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

@bind("CSYR")
@external
def csyr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("CSYRFS")
@external
def csyrfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYRFSX")
@external
def csyrfsx(
    UPLO: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYSV")
@external
def csysv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYSV_AA")
@external
def csysv_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYSV_AA_2STAGE")
@external
def csysv_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex64[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYSV_RK")
@external
def csysv_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYSV_ROOK")
@external
def csysv_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYSVX")
@external
def csysvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYSVXX")
@external
def csysvxx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    RPVGRW: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYSWAPR")
@external
def csyswapr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex64[LDA, N], ORDER_F],
    LDA: Ref(Int32),
    I1: Ref(Int32),
    I2: Ref(Int32)
) -> None: ...

@bind("CSYTF2")
@external
def csytf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTF2_RK")
@external
def csytf2_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTF2_ROOK")
@external
def csytf2_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRF")
@external
def csytrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRF_AA")
@external
def csytrf_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRF_AA_2STAGE")
@external
def csytrf_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex64[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRF_RK")
@external
def csytrf_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRF_ROOK")
@external
def csytrf_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRI")
@external
def csytri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRI2")
@external
def csytri2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRI2X")
@external
def csytri2x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRI_3")
@external
def csytri_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRI_3X")
@external
def csytri_3x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRI_ROOK")
@external
def csytri_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRS")
@external
def csytrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRS2")
@external
def csytrs2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRS_3")
@external
def csytrs_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRS_AA")
@external
def csytrs_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRS_AA_2STAGE")
@external
def csytrs_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex64[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CSYTRS_ROOK")
@external
def csytrs_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTBCON")
@external
def ctbcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTBRFS")
@external
def ctbrfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTBTRS")
@external
def ctbtrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTFSM")
@external
def ctfsm(
    TRANSR: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    B: Annotated[Complex64[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Ref(Int32)
) -> None: ...

@bind("CTFTRI")
@external
def ctftri(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTFTTP")
@external
def ctfttp(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    AP: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTFTTR")
@external
def ctfttr(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    A: Annotated[Complex64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTGEVC")
@external
def ctgevc(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    S: Complex64[LDS, Flat],
    LDS: Ref(Int32),
    P: Complex64[LDP, Flat],
    LDP: Ref(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTGEX2")
@external
def ctgex2(
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    J1: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTGEXC")
@external
def ctgexc(
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    IFST: Ref(Int32),
    ILST: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTGSEN")
@external
def ctgsen(
    IJOB: Ref(Int32),
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ref(Int32),
    M: Ref(Int32),
    PL: Ref(Float32),
    PR: Ref(Float32),
    DIF: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTGSJA")
@external
def ctgsja(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    TOLA: Ref(Float32),
    TOLB: Ref(Float32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Complex64[Flat],
    NCYCLE: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTGSNA")
@external
def ctgsna(
    JOB: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    S: Float32[Flat],
    DIF: Float32[Flat],
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTGSY2")
@external
def ctgsy2(
    TRANS: Ref(Const(String[1])),
    IJOB: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    D: Complex64[LDD, Flat],
    LDD: Ref(Int32),
    E: Complex64[LDE, Flat],
    LDE: Ref(Int32),
    F: Complex64[LDF, Flat],
    LDF: Ref(Int32),
    SCALE: Ref(Float32),
    RDSUM: Ref(Float32),
    RDSCAL: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTGSYL")
@external
def ctgsyl(
    TRANS: Ref(Const(String[1])),
    IJOB: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    D: Complex64[LDD, Flat],
    LDD: Ref(Int32),
    E: Complex64[LDE, Flat],
    LDE: Ref(Int32),
    F: Complex64[LDF, Flat],
    LDF: Ref(Int32),
    SCALE: Ref(Float32),
    DIF: Ref(Float32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPCON")
@external
def ctpcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPLQT")
@external
def ctplqt(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    MB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPLQT2")
@external
def ctplqt2(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPMLQT")
@external
def ctpmlqt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    MB: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPMQRT")
@external
def ctpmqrt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    NB: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPQRT")
@external
def ctpqrt(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPQRT2")
@external
def ctpqrt2(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPRFB")
@external
def ctprfb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("CTPRFS")
@external
def ctprfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPTRI")
@external
def ctptri(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPTRS")
@external
def ctptrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPTTF")
@external
def ctpttf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Annotated[Complex64[Flat], SourceDims("0:*")],
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTPTTR")
@external
def ctpttr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRCON")
@external
def ctrcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    RCOND: Ref(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTREVC")
@external
def ctrevc(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTREVC3")
@external
def ctrevc3(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTREXC")
@external
def ctrexc(
    COMPQ: Ref(Const(String[1])),
    N: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    IFST: Ref(Int32),
    ILST: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRRFS")
@external
def ctrrfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRSEN")
@external
def ctrsen(
    JOB: Ref(Const(String[1])),
    COMPQ: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    W: Complex64[Flat],
    M: Ref(Int32),
    S: Ref(Float32),
    SEP: Ref(Float32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRSNA")
@external
def ctrsna(
    JOB: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ref(Int32),
    S: Float32[Flat],
    SEP: Float32[Flat],
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Ref(Int32),
    RWORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRSYL")
@external
def ctrsyl(
    TRANA: Ref(Const(String[1])),
    TRANB: Ref(Const(String[1])),
    ISGN: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    SCALE: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRSYL3")
@external
def ctrsyl3(
    TRANA: Ref(Const(String[1])),
    TRANB: Ref(Const(String[1])),
    ISGN: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    SCALE: Ref(Float32),
    SWORK: Float32[LDSWORK, Flat],
    LDSWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRTI2")
@external
def ctrti2(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRTRI")
@external
def ctrtri(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRTRS")
@external
def ctrtrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRTTF")
@external
def ctrttf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ref(Int32),
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTRTTP")
@external
def ctrttp(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    AP: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CTZRZF")
@external
def ctzrzf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNBDB")
@external
def cunbdb(
    TRANS: Ref(Const(String[1])),
    SIGNS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ref(Int32),
    X12: Complex64[LDX12, Flat],
    LDX12: Ref(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ref(Int32),
    X22: Complex64[LDX22, Flat],
    LDX22: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    TAUQ2: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNBDB1")
@external
def cunbdb1(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNBDB2")
@external
def cunbdb2(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNBDB3")
@external
def cunbdb3(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNBDB4")
@external
def cunbdb4(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    PHANTOM: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNBDB5")
@external
def cunbdb5(
    M1: Ref(Int32),
    M2: Ref(Int32),
    N: Ref(Int32),
    X1: Complex64[Flat],
    INCX1: Ref(Int32),
    X2: Complex64[Flat],
    INCX2: Ref(Int32),
    Q1: Complex64[LDQ1, Flat],
    LDQ1: Ref(Int32),
    Q2: Complex64[LDQ2, Flat],
    LDQ2: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNBDB6")
@external
def cunbdb6(
    M1: Ref(Int32),
    M2: Ref(Int32),
    N: Ref(Int32),
    X1: Complex64[Flat],
    INCX1: Ref(Int32),
    X2: Complex64[Flat],
    INCX2: Ref(Int32),
    Q1: Complex64[LDQ1, Flat],
    LDQ1: Ref(Int32),
    Q2: Complex64[LDQ2, Flat],
    LDQ2: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNCSD")
@external
def cuncsd(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    JOBV2T: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    SIGNS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ref(Int32),
    X12: Complex64[LDX12, Flat],
    LDX12: Ref(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ref(Int32),
    X22: Complex64[LDX22, Flat],
    LDX22: Ref(Int32),
    THETA: Float32[Flat],
    U1: Complex64[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Complex64[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Complex64[LDV1T, Flat],
    LDV1T: Ref(Int32),
    V2T: Complex64[LDV2T, Flat],
    LDV2T: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNCSD2BY1")
@external
def cuncsd2by1(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float32[Flat],
    U1: Complex64[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Complex64[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Complex64[LDV1T, Flat],
    LDV1T: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNG2L")
@external
def cung2l(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNG2R")
@external
def cung2r(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGBR")
@external
def cungbr(
    VECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGHR")
@external
def cunghr(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGL2")
@external
def cungl2(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGLQ")
@external
def cunglq(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGQL")
@external
def cungql(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGQR")
@external
def cungqr(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGR2")
@external
def cungr2(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGRQ")
@external
def cungrq(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGTR")
@external
def cungtr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGTSQR")
@external
def cungtsqr(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNGTSQR_ROW")
@external
def cungtsqr_row(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNHR_COL")
@external
def cunhr_col(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ref(Int32),
    D: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNM22")
@external
def cunm22(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    N2: Ref(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNM2L")
@external
def cunm2l(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNM2R")
@external
def cunm2r(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNMBR")
@external
def cunmbr(
    VECT: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNMHR")
@external
def cunmhr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNML2")
@external
def cunml2(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNMLQ")
@external
def cunmlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNMQL")
@external
def cunmql(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNMQR")
@external
def cunmqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNMR2")
@external
def cunmr2(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNMR3")
@external
def cunmr3(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNMRQ")
@external
def cunmrq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNMRZ")
@external
def cunmrz(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUNMTR")
@external
def cunmtr(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("CUPGTR")
@external
def cupgtr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    TAU: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("CUPMTR")
@external
def cupmtr(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    AP: Complex64[Flat],
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DBBCSD")
@external
def dbbcsd(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    JOBV2T: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    U1: Float64[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Float64[LDV1T, Flat],
    LDV1T: Ref(Int32),
    V2T: Float64[LDV2T, Flat],
    LDV2T: Ref(Int32),
    B11D: Float64[Flat],
    B11E: Float64[Flat],
    B12D: Float64[Flat],
    B12E: Float64[Flat],
    B21D: Float64[Flat],
    B21E: Float64[Flat],
    B22D: Float64[Flat],
    B22E: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DBDSDC")
@external
def dbdsdc(
    UPLO: Ref(Const(String[1])),
    COMPQ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ref(Int32),
    Q: Float64[Flat],
    IQ: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DBDSQR")
@external
def dbdsqr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NCVT: Ref(Int32),
    NRU: Ref(Int32),
    NCC: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VT: Float64[LDVT, Flat],
    LDVT: Ref(Int32),
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DBDSVDX")
@external
def dbdsvdx(
    UPLO: Ref(Const(String[1])),
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    NS: Ref(Int32),
    S: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DDISNA")
@external
def ddisna(
    JOB: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    D: Float64[Flat],
    SEP: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBBRD")
@external
def dgbbrd(
    VECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NCC: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    PT: Float64[LDPT, Flat],
    LDPT: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBCON")
@external
def dgbcon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBEQU")
@external
def dgbequ(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBEQUB")
@external
def dgbequb(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBRFS")
@external
def dgbrfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBRFSX")
@external
def dgbrfsx(
    TRANS: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBSV")
@external
def dgbsv(
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBSVX")
@external
def dgbsvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBSVXX")
@external
def dgbsvxx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    RPVGRW: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBTF2")
@external
def dgbtf2(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBTRF")
@external
def dgbtrf(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGBTRS")
@external
def dgbtrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEBAK")
@external
def dgebak(
    JOB: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float64[Flat],
    M: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEBAL")
@external
def dgebal(
    JOB: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEBD2")
@external
def dgebd2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Float64[Flat],
    TAUP: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEBRD")
@external
def dgebrd(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Float64[Flat],
    TAUP: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGECON")
@external
def dgecon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Arg(7), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Ref(Arg(11)), Ref(Arg(12)), Return('K', 0), Arg(13), Arg(14), Arg(15), Ref(Arg(16)), Arg(17), Arg(18), Ref(Arg(19)), Arg(20), Ref(Arg(21)), Arg(22), Ref(Arg(23)), Arg(24), Ref(Arg(25)), Arg(26), Ref(Arg(27)), Return('INFO', 10)])
def dgedmd(
    JOBS: Ref(Const(String[1])),
    JOBZ: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBF: Ref(Const(String[1])),
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
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Ref(Arg(6)), Ref(Arg(7)), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Arg(11), Ref(Arg(12)), Arg(13), Ref(Arg(14)), Ref(Arg(15)), Ref(Arg(16)), Return('K', 2), Arg(17), Arg(18), Arg(19), Ref(Arg(20)), Arg(21), Arg(22), Ref(Arg(23)), Arg(24), Ref(Arg(25)), Arg(26), Ref(Arg(27)), Arg(28), Ref(Arg(29)), Arg(30), Ref(Arg(31)), Return('INFO', 12)])
def dgedmdq(
    JOBS: Ref(Const(String[1])),
    JOBZ: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    JOBT: Ref(Const(String[1])),
    JOBF: Ref(Const(String[1])),
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
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEEQUB")
@external
def dgeequb(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEES")
@external
def dgees(
    JOBVS: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELECT: Ref(Bool),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    SDIM: Ref(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VS: Float64[LDVS, Flat],
    LDVS: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEESX")
@external
def dgeesx(
    JOBVS: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELECT: Ref(Bool),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    SDIM: Ref(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VS: Float64[LDVS, Flat],
    LDVS: Ref(Int32),
    RCONDE: Ref(Float64),
    RCONDV: Ref(Float64),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEEV")
@external
def dgeev(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEEVX")
@external
def dgeevx(
    BALANC: Ref(Const(String[1])),
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float64[Flat],
    ABNRM: Ref(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEHD2")
@external
def dgehd2(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEHRD")
@external
def dgehrd(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEJSV")
@external
def dgejsv(
    JOBA: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBT: Ref(Const(String[1])),
    JOBP: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    SVA: Float64[N],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    WORK: Float64[LWORK],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGELQ")
@external
def dgelq(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[Flat],
    TSIZE: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGELQ2")
@external
def dgelq2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGELQF")
@external
def dgelqf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGELQT")
@external
def dgelqt(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGELQT3")
@external
def dgelqt3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGELS")
@external
def dgels(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGELSD")
@external
def dgelsd(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    S: Float64[Flat],
    RCOND: Ref(Float64),
    RANK: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGELSS")
@external
def dgelss(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    S: Float64[Flat],
    RCOND: Ref(Float64),
    RANK: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGELST")
@external
def dgelst(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGELSY")
@external
def dgelsy(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    JPVT: Int32[Flat],
    RCOND: Ref(Float64),
    RANK: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEMLQ")
@external
def dgemlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[Flat],
    TSIZE: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEMLQT")
@external
def dgemlqt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEMQR")
@external
def dgemqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[Flat],
    TSIZE: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEMQRT")
@external
def dgemqrt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    NB: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQL2")
@external
def dgeql2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQLF")
@external
def dgeqlf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQP3")
@external
def dgeqp3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQP3RK")
@external
def dgeqp3rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    KMAX: Ref(Int32),
    ABSTOL: Ref(Float64),
    RELTOL: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    K: Ref(Int32),
    MAXC2NRMK: Ref(Float64),
    RELMAXC2NRMK: Ref(Float64),
    JPIV: Int32[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQR")
@external
def dgeqr(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[Flat],
    TSIZE: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQR2")
@external
def dgeqr2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQR2P")
@external
def dgeqr2p(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQRF")
@external
def dgeqrf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQRFP")
@external
def dgeqrfp(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQRT")
@external
def dgeqrt(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQRT2")
@external
def dgeqrt2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGEQRT3")
@external
def dgeqrt3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGERFS")
@external
def dgerfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGERFSX")
@external
def dgerfsx(
    TRANS: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGERQ2")
@external
def dgerq2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGERQF")
@external
def dgerqf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGESC2")
@external
def dgesc2(
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    RHS: Float64[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Ref(Float64)
) -> None: ...

@bind("DGESDD")
@external
def dgesdd(
    JOBZ: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGESV")
@external
def dgesv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGESVD")
@external
def dgesvd(
    JOBU: Ref(Const(String[1])),
    JOBVT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGESVDQ")
@external
def dgesvdq(
    JOBA: Ref(Const(String[1])),
    JOBP: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    NUMRANK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGESVDX")
@external
def dgesvdx(
    JOBU: Ref(Const(String[1])),
    JOBVT: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    NS: Ref(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGESVJ")
@external
def dgesvj(
    JOBA: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    SVA: Float64[N],
    MV: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    WORK: Float64[LWORK],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGESVX")
@external
def dgesvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGESVXX")
@external
def dgesvxx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    RPVGRW: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGETC2")
@external
def dgetc2(
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGETF2")
@external
def dgetf2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGETRF")
@external
def dgetrf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGETRF2")
@external
def dgetrf2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGETRI")
@external
def dgetri(
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGETRS")
@external
def dgetrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGETSLS")
@external
def dgetsls(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGETSQRHRT")
@external
def dgetsqrhrt(
    M: Ref(Int32),
    N: Ref(Int32),
    MB1: Ref(Int32),
    NB1: Ref(Int32),
    NB2: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGBAK")
@external
def dggbak(
    JOB: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    M: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGBAL")
@external
def dggbal(
    JOB: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGES")
@external
def dgges(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VSL: Float64[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Float64[LDVSR, Flat],
    LDVSR: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGES3")
@external
def dgges3(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VSL: Float64[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Float64[LDVSR, Flat],
    LDVSR: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGESX")
@external
def dggesx(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VSL: Float64[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Float64[LDVSR, Flat],
    LDVSR: Ref(Int32),
    RCONDE: Float64[2],
    RCONDV: Float64[2],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGEV")
@external
def dggev(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGEV3")
@external
def dggev3(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGEVX")
@external
def dggevx(
    BALANC: Ref(Const(String[1])),
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    ABNRM: Ref(Float64),
    BBNRM: Ref(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGGLM")
@external
def dggglm(
    N: Ref(Int32),
    M: Ref(Int32),
    P: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    D: Float64[Flat],
    X: Float64[Flat],
    Y: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGHD3")
@external
def dgghd3(
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGHRD")
@external
def dgghrd(
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGLSE")
@external
def dgglse(
    M: Ref(Int32),
    N: Ref(Int32),
    P: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    C: Float64[Flat],
    D: Float64[Flat],
    X: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGQRF")
@external
def dggqrf(
    N: Ref(Int32),
    M: Ref(Int32),
    P: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAUA: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    TAUB: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGRQF")
@external
def dggrqf(
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAUA: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    TAUB: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGSVD3")
@external
def dggsvd3(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    P: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGGSVP3")
@external
def dggsvp3(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    TOLA: Ref(Float64),
    TOLB: Ref(Float64),
    K: Ref(Int32),
    L: Ref(Int32),
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    IWORK: Int32[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGSVJ0")
@external
def dgsvj0(
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[N],
    SVA: Float64[N],
    MV: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    EPS: Ref(Float64),
    SFMIN: Ref(Float64),
    TOL: Ref(Float64),
    NSWEEP: Ref(Int32),
    WORK: Float64[LWORK],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGSVJ1")
@external
def dgsvj1(
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[N],
    SVA: Float64[N],
    MV: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    EPS: Ref(Float64),
    SFMIN: Ref(Float64),
    TOL: Ref(Float64),
    NSWEEP: Ref(Int32),
    WORK: Float64[LWORK],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGTCON")
@external
def dgtcon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGTRFS")
@external
def dgtrfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DLF: Float64[Flat],
    DF: Float64[Flat],
    DUF: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGTSV")
@external
def dgtsv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGTSVX")
@external
def dgtsvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DLF: Float64[Flat],
    DF: Float64[Flat],
    DUF: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGTTRF")
@external
def dgttrf(
    N: Ref(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DGTTRS")
@external
def dgttrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DGTTS2")
@external
def dgtts2(
    ITRANS: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("DHGEQZ")
@external
def dhgeqz(
    JOB: Ref(Const(String[1])),
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DHSEIN")
@external
def dhsein(
    SIDE: Ref(Const(String[1])),
    EIGSRC: Ref(Const(String[1])),
    INITV: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float64[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DHSEQR")
@external
def dhseqr(
    JOB: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DISNAN")
@external
@native_call([Ref(Arg(0))])
def disnan(
    DIN: Const(Float64)
) -> Bool: ...

@bind("DLA_GBAMV")
@external
def dla_gbamv(
    TRANS: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    ALPHA: Ref(Float64),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float64),
    Y: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("DLA_GBRCOND")
@external
def dla_gbrcond(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    CMODE: Ref(Int32),
    C: Float64[Flat],
    INFO: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_GBRFSX_EXTENDED")
@external
def dla_gbrfsx_extended(
    PREC_TYPE: Ref(Int32),
    TRANS_TYPE: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    Y: Float64[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Ref(Float64),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float64),
    DZ_UB: Ref(Float64),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLA_GBRPVGRW")
@external
def dla_gbrpvgrw(
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NCOLS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ref(Int32)
) -> Float64: ...

@bind("DLA_GEAMV")
@external
def dla_geamv(
    TRANS: Ref(Int32),
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

@bind("DLA_GERCOND")
@external
def dla_gercond(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    CMODE: Ref(Int32),
    C: Float64[Flat],
    INFO: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_GERFSX_EXTENDED")
@external
def dla_gerfsx_extended(
    PREC_TYPE: Ref(Int32),
    TRANS_TYPE: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    Y: Float64[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ref(Int32),
    ERRS_N: Float64[NRHS, Flat],
    ERRS_C: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Ref(Float64),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float64),
    DZ_UB: Ref(Float64),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLA_GERPVGRW")
@external
def dla_gerpvgrw(
    N: Ref(Int32),
    NCOLS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32)
) -> Float64: ...

@bind("DLA_LIN_BERR")
@external
def dla_lin_berr(
    N: Ref(Int32),
    NZ: Ref(Int32),
    NRHS: Ref(Int32),
    RES: Annotated[Float64[N, NRHS], ORDER_F],
    AYB: Annotated[Float64[N, NRHS], ORDER_F],
    BERR: Float64[NRHS]
) -> None: ...

@bind("DLA_PORCOND")
@external
def dla_porcond(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    CMODE: Ref(Int32),
    C: Float64[Flat],
    INFO: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_PORFSX_EXTENDED")
@external
def dla_porfsx_extended(
    PREC_TYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    COLEQU: Ref(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    Y: Float64[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Ref(Float64),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float64),
    DZ_UB: Ref(Float64),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLA_PORPVGRW")
@external
def dla_porpvgrw(
    UPLO: Ref(Const(String[1])),
    NCOLS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLA_SYAMV")
@external
def dla_syamv(
    UPLO: Ref(Int32),
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

@bind("DLA_SYRCOND")
@external
def dla_syrcond(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    CMODE: Ref(Int32),
    C: Float64[Flat],
    INFO: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_SYRFSX_EXTENDED")
@external
def dla_syrfsx_extended(
    PREC_TYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    Y: Float64[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Ref(Float64),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float64),
    DZ_UB: Ref(Float64),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLA_SYRPVGRW")
@external
def dla_syrpvgrw(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    INFO: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLA_WWADDW")
@external
def dla_wwaddw(
    N: Ref(Int32),
    X: Float64[Flat],
    Y: Float64[Flat],
    W: Float64[Flat]
) -> None: ...

@bind("DLABAD")
@external
def dlabad(
    SMALL: Ref(Float64),
    LARGE: Ref(Float64)
) -> None: ...

@bind("DLABRD")
@external
def dlabrd(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Float64[Flat],
    TAUP: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    Y: Float64[LDY, Flat],
    LDY: Ref(Int32)
) -> None: ...

@bind("DLACN2")
@external
def dlacn2(
    N: Ref(Int32),
    V: Float64[Flat],
    X: Float64[Flat],
    ISGN: Int32[Flat],
    EST: Ref(Float64),
    KASE: Ref(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("DLACON")
@external
def dlacon(
    N: Ref(Int32),
    V: Float64[Flat],
    X: Float64[Flat],
    ISGN: Int32[Flat],
    EST: Ref(Float64),
    KASE: Ref(Int32)
) -> None: ...

@bind("DLACPY")
@external
def dlacpy(
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("DLADIV")
@external
def dladiv(
    A: Ref(Float64),
    B: Ref(Float64),
    C: Ref(Float64),
    D: Ref(Float64),
    P: Ref(Float64),
    Q: Ref(Float64)
) -> None: ...

@bind("DLADIV1")
@external
def dladiv1(
    A: Ref(Float64),
    B: Ref(Float64),
    C: Ref(Float64),
    D: Ref(Float64),
    P: Ref(Float64),
    Q: Ref(Float64)
) -> None: ...

@bind("DLADIV2")
@external
def dladiv2(
    A: Ref(Float64),
    B: Ref(Float64),
    C: Ref(Float64),
    D: Ref(Float64),
    R: Ref(Float64),
    T: Ref(Float64)
) -> Float64: ...

@bind("DLAE2")
@external
def dlae2(
    A: Ref(Float64),
    B: Ref(Float64),
    C: Ref(Float64),
    RT1: Ref(Float64),
    RT2: Ref(Float64)
) -> None: ...

@bind("DLAEBZ")
@external
def dlaebz(
    IJOB: Ref(Int32),
    NITMAX: Ref(Int32),
    N: Ref(Int32),
    MMAX: Ref(Int32),
    MINP: Ref(Int32),
    NBMIN: Ref(Int32),
    ABSTOL: Ref(Float64),
    RELTOL: Ref(Float64),
    PIVMIN: Ref(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    NVAL: Int32[Flat],
    AB: Float64[MMAX, Flat],
    C: Float64[Flat],
    MOUT: Ref(Int32),
    NAB: Int32[MMAX, Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAED0")
@external
def dlaed0(
    ICOMPQ: Ref(Int32),
    QSIZ: Ref(Int32),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    QSTORE: Float64[LDQS, Flat],
    LDQS: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAED1")
@external
def dlaed1(
    N: Ref(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    INDXQ: Int32[Flat],
    RHO: Ref(Float64),
    CUTPNT: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAED2")
@external
def dlaed2(
    K: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    INDXQ: Int32[Flat],
    RHO: Ref(Float64),
    Z: Float64[Flat],
    DLAMBDA: Float64[Flat],
    W: Float64[Flat],
    Q2: Float64[Flat],
    INDX: Int32[Flat],
    INDXC: Int32[Flat],
    INDXP: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAED3")
@external
def dlaed3(
    K: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    RHO: Ref(Float64),
    DLAMBDA: Float64[Flat],
    Q2: Float64[Flat],
    INDX: Int32[Flat],
    CTOT: Int32[Flat],
    W: Float64[Flat],
    S: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAED4")
@external
def dlaed4(
    N: Ref(Int32),
    I: Ref(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    DELTA: Float64[Flat],
    RHO: Ref(Float64),
    DLAM: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAED5")
@external
def dlaed5(
    I: Ref(Int32),
    D: Float64[2],
    Z: Float64[2],
    DELTA: Float64[2],
    RHO: Ref(Float64),
    DLAM: Ref(Float64)
) -> None: ...

@bind("DLAED6")
@external
def dlaed6(
    KNITER: Ref(Int32),
    ORGATI: Ref(Bool),
    RHO: Ref(Float64),
    D: Float64[3],
    Z: Float64[3],
    FINIT: Ref(Float64),
    TAU: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAED7")
@external
def dlaed7(
    ICOMPQ: Ref(Int32),
    N: Ref(Int32),
    QSIZ: Ref(Int32),
    TLVLS: Ref(Int32),
    CURLVL: Ref(Int32),
    CURPBM: Ref(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    INDXQ: Int32[Flat],
    RHO: Ref(Float64),
    CUTPNT: Ref(Int32),
    QSTORE: Float64[Flat],
    QPTR: Int32[Flat],
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAED8")
@external
def dlaed8(
    ICOMPQ: Ref(Int32),
    K: Ref(Int32),
    N: Ref(Int32),
    QSIZ: Ref(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    INDXQ: Int32[Flat],
    RHO: Ref(Float64),
    CUTPNT: Ref(Int32),
    Z: Float64[Flat],
    DLAMBDA: Float64[Flat],
    Q2: Float64[LDQ2, Flat],
    LDQ2: Ref(Int32),
    W: Float64[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAED9")
@external
def dlaed9(
    K: Ref(Int32),
    KSTART: Ref(Int32),
    KSTOP: Ref(Int32),
    N: Ref(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    RHO: Ref(Float64),
    DLAMBDA: Float64[Flat],
    W: Float64[Flat],
    S: Float64[LDS, Flat],
    LDS: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAEDA")
@external
def dlaeda(
    N: Ref(Int32),
    TLVLS: Ref(Int32),
    CURLVL: Ref(Int32),
    CURPBM: Ref(Int32),
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    Q: Float64[Flat],
    QPTR: Int32[Flat],
    Z: Float64[Flat],
    ZTEMP: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAEIN")
@external
def dlaein(
    RIGHTV: Ref(Bool),
    NOINIT: Ref(Bool),
    N: Ref(Int32),
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    WR: Ref(Float64),
    WI: Ref(Float64),
    VR: Float64[Flat],
    VI: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    EPS3: Ref(Float64),
    SMLNUM: Ref(Float64),
    BIGNUM: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAEV2")
@external
def dlaev2(
    A: Ref(Float64),
    B: Ref(Float64),
    C: Ref(Float64),
    RT1: Ref(Float64),
    RT2: Ref(Float64),
    CS1: Ref(Float64),
    SN1: Ref(Float64)
) -> None: ...

@bind("DLAEXC")
@external
def dlaexc(
    WANTQ: Ref(Bool),
    N: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    J1: Ref(Int32),
    N1: Ref(Int32),
    N2: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAG2")
@external
def dlag2(
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    SAFMIN: Ref(Float64),
    SCALE1: Ref(Float64),
    SCALE2: Ref(Float64),
    WR1: Ref(Float64),
    WR2: Ref(Float64),
    WI: Ref(Float64)
) -> None: ...

@bind("DLAG2S")
@external
def dlag2s(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    SA: Float32[LDSA, Flat],
    LDSA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAGS2")
@external
def dlags2(
    UPPER: Ref(Bool),
    A1: Ref(Float64),
    A2: Ref(Float64),
    A3: Ref(Float64),
    B1: Ref(Float64),
    B2: Ref(Float64),
    B3: Ref(Float64),
    CSU: Ref(Float64),
    SNU: Ref(Float64),
    CSV: Ref(Float64),
    SNV: Ref(Float64),
    CSQ: Ref(Float64),
    SNQ: Ref(Float64)
) -> None: ...

@bind("DLAGTF")
@external
def dlagtf(
    N: Ref(Int32),
    A: Float64[Flat],
    LAMBDA: Ref(Float64),
    B: Float64[Flat],
    C: Float64[Flat],
    TOL: Ref(Float64),
    D: Float64[Flat],
    IN: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAGTM")
@external
def dlagtm(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    ALPHA: Ref(Float64),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    BETA: Ref(Float64),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("DLAGTS")
@external
def dlagts(
    JOB: Ref(Int32),
    N: Ref(Int32),
    A: Float64[Flat],
    B: Float64[Flat],
    C: Float64[Flat],
    D: Float64[Flat],
    IN: Int32[Flat],
    Y: Float64[Flat],
    TOL: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAGV2")
@external
def dlagv2(
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHAR: Float64[2],
    ALPHAI: Float64[2],
    BETA: Float64[2],
    CSL: Ref(Float64),
    SNL: Ref(Float64),
    CSR: Ref(Float64),
    SNR: Ref(Float64)
) -> None: ...

@bind("DLAHQR")
@external
def dlahqr(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAHR2")
@external
def dlahr2(
    N: Ref(Int32),
    K: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[NB],
    T: Annotated[Float64[LDT, NB], ORDER_F],
    LDT: Ref(Int32),
    Y: Annotated[Float64[LDY, NB], ORDER_F],
    LDY: Ref(Int32)
) -> None: ...

@bind("DLAIC1")
@external
def dlaic1(
    JOB: Ref(Int32),
    J: Ref(Int32),
    X: Float64[J],
    SEST: Ref(Float64),
    W: Float64[J],
    GAMMA: Ref(Float64),
    SESTPR: Ref(Float64),
    S: Ref(Float64),
    C: Ref(Float64)
) -> None: ...

@bind("DLAISNAN")
@external
@native_call([Ref(Arg(0)), Ref(Arg(1))])
def dlaisnan(
    DIN1: Const(Float64),
    DIN2: Const(Float64)
) -> Bool: ...

@bind("DLALN2")
@external
def dlaln2(
    LTRANS: Ref(Bool),
    NA: Ref(Int32),
    NW: Ref(Int32),
    SMIN: Ref(Float64),
    CA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D1: Ref(Float64),
    D2: Ref(Float64),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WR: Ref(Float64),
    WI: Ref(Float64),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    SCALE: Ref(Float64),
    XNORM: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLALS0")
@external
def dlals0(
    ICOMPQ: Ref(Int32),
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    NRHS: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    BX: Float64[LDBX, Flat],
    LDBX: Ref(Int32),
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Ref(Int32),
    POLES: Float64[LDGNUM, Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[LDGNUM, Flat],
    Z: Float64[Flat],
    K: Ref(Int32),
    C: Ref(Float64),
    S: Ref(Float64),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLALSA")
@external
def dlalsa(
    ICOMPQ: Ref(Int32),
    SMLSIZ: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    BX: Float64[LDBX, Flat],
    LDBX: Ref(Int32),
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float64[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float64[LDU, Flat],
    DIFR: Float64[LDU, Flat],
    Z: Float64[LDU, Flat],
    POLES: Float64[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float64[LDU, Flat],
    C: Float64[Flat],
    S: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLALSD")
@external
def dlalsd(
    UPLO: Ref(Const(String[1])),
    SMLSIZ: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    RCOND: Ref(Float64),
    RANK: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAMRG")
@external
def dlamrg(
    N1: Ref(Int32),
    N2: Ref(Int32),
    A: Float64[Flat],
    DTRD1: Ref(Int32),
    DTRD2: Ref(Int32),
    INDEX: Int32[Flat]
) -> None: ...

@bind("DLAMSWLQ")
@external
def dlamswlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAMTSQR")
@external
def dlamtsqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLANEG")
@external
def dlaneg(
    N: Ref(Int32),
    D: Float64[Flat],
    LLD: Float64[Flat],
    SIGMA: Ref(Float64),
    PIVMIN: Ref(Float64),
    R: Ref(Int32)
) -> Int32: ...

@bind("DLANGB")
@external
def dlangb(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANGE")
@external
def dlange(
    NORM: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANGT")
@external
def dlangt(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat]
) -> Float64: ...

@bind("DLANHS")
@external
def dlanhs(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANSB")
@external
def dlansb(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANSF")
@external
def dlansf(
    NORM: Ref(Const(String[1])),
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    WORK: Annotated[Float64[Flat], SourceDims("0:*")]
) -> Float64: ...

@bind("DLANSP")
@external
def dlansp(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANST")
@external
def dlanst(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat]
) -> Float64: ...

@bind("DLANSY")
@external
def dlansy(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANTB")
@external
def dlantb(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANTP")
@external
def dlantp(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANTR")
@external
def dlantr(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANV2")
@external
def dlanv2(
    A: Ref(Float64),
    B: Ref(Float64),
    C: Ref(Float64),
    D: Ref(Float64),
    RT1R: Ref(Float64),
    RT1I: Ref(Float64),
    RT2R: Ref(Float64),
    RT2I: Ref(Float64),
    CS: Ref(Float64),
    SN: Ref(Float64)
) -> None: ...

@bind("DLAORHR_COL_GETRFNP")
@external
def dlaorhr_col_getrfnp(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAORHR_COL_GETRFNP2")
@external
def dlaorhr_col_getrfnp2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAPLL")
@external
def dlapll(
    N: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32),
    Y: Float64[Flat],
    INCY: Ref(Int32),
    SSMIN: Ref(Float64)
) -> None: ...

@bind("DLAPMR")
@external
def dlapmr(
    FORWRD: Ref(Bool),
    M: Ref(Int32),
    N: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("DLAPMT")
@external
def dlapmt(
    FORWRD: Ref(Bool),
    M: Ref(Int32),
    N: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("DLAPY2")
@external
def dlapy2(
    X: Ref(Float64),
    Y: Ref(Float64)
) -> Float64: ...

@bind("DLAPY3")
@external
def dlapy3(
    X: Ref(Float64),
    Y: Ref(Float64),
    Z: Ref(Float64)
) -> Float64: ...

@bind("DLAQGB")
@external
def dlaqgb(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("DLAQGE")
@external
def dlaqge(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("DLAQP2")
@external
def dlaqp2(
    M: Ref(Int32),
    N: Ref(Int32),
    OFFSET: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Float64[Flat]
) -> None: ...

@bind("DLAQP2RK")
@external
def dlaqp2rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    IOFFSET: Ref(Int32),
    KMAX: Ref(Int32),
    ABSTOL: Ref(Float64),
    RELTOL: Ref(Float64),
    KP1: Ref(Int32),
    MAXC2NRM: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    K: Ref(Int32),
    MAXC2NRMK: Ref(Float64),
    RELMAXC2NRMK: Ref(Float64),
    JPIV: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAQP3RK")
@external
def dlaqp3rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    IOFFSET: Ref(Int32),
    NB: Ref(Int32),
    ABSTOL: Ref(Float64),
    RELTOL: Ref(Float64),
    KP1: Ref(Int32),
    MAXC2NRM: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    DONE: Ref(Bool),
    KB: Ref(Int32),
    MAXC2NRMK: Ref(Float64),
    RELMAXC2NRMK: Ref(Float64),
    JPIV: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Float64[Flat],
    F: Float64[LDF, Flat],
    LDF: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAQPS")
@external
def dlaqps(
    M: Ref(Int32),
    N: Ref(Int32),
    OFFSET: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Float64[Flat],
    F: Float64[LDF, Flat],
    LDF: Ref(Int32)
) -> None: ...

@bind("DLAQR0")
@external
def dlaqr0(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAQR1")
@external
def dlaqr1(
    N: Ref(Int32),
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    SR1: Ref(Float64),
    SI1: Ref(Float64),
    SR2: Ref(Float64),
    SI2: Ref(Float64),
    V: Float64[Flat]
) -> None: ...

@bind("DLAQR2")
@external
def dlaqr2(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NW: Ref(Int32),
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    NS: Ref(Int32),
    ND: Ref(Int32),
    SR: Float64[Flat],
    SI: Float64[Flat],
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    NH: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    NV: Ref(Int32),
    WV: Float64[LDWV, Flat],
    LDWV: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32)
) -> None: ...

@bind("DLAQR3")
@external
def dlaqr3(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NW: Ref(Int32),
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    NS: Ref(Int32),
    ND: Ref(Int32),
    SR: Float64[Flat],
    SI: Float64[Flat],
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    NH: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    NV: Ref(Int32),
    WV: Float64[LDWV, Flat],
    LDWV: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32)
) -> None: ...

@bind("DLAQR4")
@external
def dlaqr4(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAQR5")
@external
def dlaqr5(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    KACC22: Ref(Int32),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NSHFTS: Ref(Int32),
    SR: Float64[Flat],
    SI: Float64[Flat],
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    NV: Ref(Int32),
    WV: Float64[LDWV, Flat],
    LDWV: Ref(Int32),
    NH: Ref(Int32),
    WH: Float64[LDWH, Flat],
    LDWH: Ref(Int32)
) -> None: ...

@bind("DLAQSB")
@external
def dlaqsb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("DLAQSP")
@external
def dlaqsp(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("DLAQSY")
@external
def dlaqsy(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("DLAQTR")
@external
def dlaqtr(
    LTRAN: Ref(Bool),
    LREAL: Ref(Bool),
    N: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    B: Float64[Flat],
    W: Ref(Float64),
    SCALE: Ref(Float64),
    X: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Arg(6), Ref(Arg(7)), Arg(8), Ref(Arg(9)), Arg(10), Arg(11), Arg(12), Arg(13), Ref(Arg(14)), Arg(15), Ref(Arg(16)), Arg(17), Ref(Arg(18)), Ref(Arg(19)), Return('INFO', 0)])
def dlaqz0(
    WANTS: Ref(Const(String[1])),
    WANTQ: Ref(Const(String[1])),
    WANTZ: Ref(Const(String[1])),
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
@native_call([Arg(0), Ref(Arg(1)), Arg(2), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Ref(Arg(7)), Ref(Arg(8)), Arg(9)])
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Arg(6), Ref(Arg(7)), Arg(8), Ref(Arg(9)), Ref(Arg(10)), Ref(Arg(11)), Arg(12), Ref(Arg(13)), Ref(Arg(14)), Ref(Arg(15)), Arg(16), Ref(Arg(17))])
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Arg(7), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Arg(11), Ref(Arg(12)), Arg(13), Ref(Arg(14)), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Arg(18), Ref(Arg(19)), Arg(20), Ref(Arg(21)), Arg(22), Ref(Arg(23)), Ref(Arg(24)), Return('INFO', 2)])
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Ref(Arg(7)), Arg(8), Arg(9), Arg(10), Arg(11), Ref(Arg(12)), Arg(13), Ref(Arg(14)), Arg(15), Ref(Arg(16)), Arg(17), Ref(Arg(18)), Arg(19), Ref(Arg(20)), Arg(21), Ref(Arg(22)), Arg(23), Ref(Arg(24)), Return('INFO', 0)])
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
    N: Ref(Int32),
    B1: Ref(Int32),
    BN: Ref(Int32),
    LAMBDA: Ref(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    LD: Float64[Flat],
    LLD: Float64[Flat],
    PIVMIN: Ref(Float64),
    GAPTOL: Ref(Float64),
    Z: Float64[Flat],
    WANTNC: Ref(Bool),
    NEGCNT: Ref(Int32),
    ZTZ: Ref(Float64),
    MINGMA: Ref(Float64),
    R: Ref(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Ref(Float64),
    RESID: Ref(Float64),
    RQCORR: Ref(Float64),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLAR2V")
@external
def dlar2v(
    N: Ref(Int32),
    X: Float64[Flat],
    Y: Float64[Flat],
    Z: Float64[Flat],
    INCX: Ref(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("DLARF")
@external
def dlarf(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Float64[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARF1F")
@external
def dlarf1f(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Float64[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARF1L")
@external
def dlarf1l(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Float64[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARFB")
@external
def dlarfb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("DLARFB_GETT")
@external
def dlarfb_gett(
    IDENT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("DLARFG")
@external
def dlarfg(
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    X: Float64[Flat],
    INCX: Ref(Int32),
    TAU: Ref(Float64)
) -> None: ...

@bind("DLARFGP")
@external
def dlarfgp(
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    X: Float64[Flat],
    INCX: Ref(Int32),
    TAU: Ref(Float64)
) -> None: ...

@bind("DLARFT")
@external
def dlarft(
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    TAU: Float64[Flat],
    T: Float64[LDT, Flat],
    LDT: Ref(Int32)
) -> None: ...

@bind("DLARFX")
@external
def dlarfx(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Float64[Flat],
    TAU: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARFY")
@external
def dlarfy(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    V: Float64[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARGV")
@external
def dlargv(
    N: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32),
    Y: Float64[Flat],
    INCY: Ref(Int32),
    C: Float64[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("DLARMM")
@external
def dlarmm(
    ANORM: Ref(Float64),
    BNORM: Ref(Float64),
    CNORM: Ref(Float64)
) -> Float64: ...

@bind("DLARNV")
@external
def dlarnv(
    IDIST: Ref(Int32),
    ISEED: Int32[4],
    N: Ref(Int32),
    X: Float64[Flat]
) -> None: ...

@bind("DLARRA")
@external
def dlarra(
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    SPLTOL: Ref(Float64),
    TNRM: Ref(Float64),
    NSPLIT: Ref(Int32),
    ISPLIT: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLARRB")
@external
def dlarrb(
    N: Ref(Int32),
    D: Float64[Flat],
    LLD: Float64[Flat],
    IFIRST: Ref(Int32),
    ILAST: Ref(Int32),
    RTOL1: Ref(Float64),
    RTOL2: Ref(Float64),
    OFFSET: Ref(Int32),
    W: Float64[Flat],
    WGAP: Float64[Flat],
    WERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Ref(Float64),
    SPDIAM: Ref(Float64),
    TWIST: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLARRC")
@external
def dlarrc(
    JOBT: Ref(Const(String[1])),
    N: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    PIVMIN: Ref(Float64),
    EIGCNT: Ref(Int32),
    LCNT: Ref(Int32),
    RCNT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLARRD")
@external
def dlarrd(
    RANGE: Ref(Const(String[1])),
    ORDER: Ref(Const(String[1])),
    N: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    GERS: Float64[Flat],
    RELTOL: Ref(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    PIVMIN: Ref(Float64),
    NSPLIT: Ref(Int32),
    ISPLIT: Int32[Flat],
    M: Ref(Int32),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WL: Ref(Float64),
    WU: Ref(Float64),
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLARRE")
@external
def dlarre(
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    RTOL1: Ref(Float64),
    RTOL2: Ref(Float64),
    SPLTOL: Ref(Float64),
    NSPLIT: Ref(Int32),
    ISPLIT: Int32[Flat],
    M: Ref(Int32),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WGAP: Float64[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float64[Flat],
    PIVMIN: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLARRF")
@external
def dlarrf(
    N: Ref(Int32),
    D: Float64[Flat],
    L: Float64[Flat],
    LD: Float64[Flat],
    CLSTRT: Ref(Int32),
    CLEND: Ref(Int32),
    W: Float64[Flat],
    WGAP: Float64[Flat],
    WERR: Float64[Flat],
    SPDIAM: Ref(Float64),
    CLGAPL: Ref(Float64),
    CLGAPR: Ref(Float64),
    PIVMIN: Ref(Float64),
    SIGMA: Ref(Float64),
    DPLUS: Float64[Flat],
    LPLUS: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLARRJ")
@external
def dlarrj(
    N: Ref(Int32),
    D: Float64[Flat],
    E2: Float64[Flat],
    IFIRST: Ref(Int32),
    ILAST: Ref(Int32),
    RTOL: Ref(Float64),
    OFFSET: Ref(Int32),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Ref(Float64),
    SPDIAM: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLARRK")
@external
def dlarrk(
    N: Ref(Int32),
    IW: Ref(Int32),
    GL: Ref(Float64),
    GU: Ref(Float64),
    D: Float64[Flat],
    E2: Float64[Flat],
    PIVMIN: Ref(Float64),
    RELTOL: Ref(Float64),
    W: Ref(Float64),
    WERR: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLARRR")
@external
def dlarrr(
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLARRV")
@external
def dlarrv(
    N: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    PIVMIN: Ref(Float64),
    ISPLIT: Int32[Flat],
    M: Ref(Int32),
    DOL: Ref(Int32),
    DOU: Ref(Int32),
    MINRGP: Ref(Float64),
    RTOL1: Ref(Float64),
    RTOL2: Ref(Float64),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WGAP: Float64[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLARSCL2")
@external
def dlarscl2(
    M: Ref(Int32),
    N: Ref(Int32),
    D: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Ref(Int32)
) -> None: ...

@bind("DLARTG")
@external
def dlartg(
    f: Ref(Float64),
    g: Ref(Float64),
    c: Ref(Float64),
    s: Ref(Float64),
    r: Ref(Float64)
) -> None: ...

@bind("DLARTGP")
@external
def dlartgp(
    F: Ref(Float64),
    G: Ref(Float64),
    CS: Ref(Float64),
    SN: Ref(Float64),
    R: Ref(Float64)
) -> None: ...

@bind("DLARTGS")
@external
def dlartgs(
    X: Ref(Float64),
    Y: Ref(Float64),
    SIGMA: Ref(Float64),
    CS: Ref(Float64),
    SN: Ref(Float64)
) -> None: ...

@bind("DLARTV")
@external
def dlartv(
    N: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32),
    Y: Float64[Flat],
    INCY: Ref(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("DLARUV")
@external
def dlaruv(
    ISEED: Int32[4],
    N: Ref(Int32),
    X: Float64[N]
) -> None: ...

@bind("DLARZ")
@external
def dlarz(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    V: Float64[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARZB")
@external
def dlarzb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("DLARZT")
@external
def dlarzt(
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    TAU: Float64[Flat],
    T: Float64[LDT, Flat],
    LDT: Ref(Int32)
) -> None: ...

@bind("DLAS2")
@external
def dlas2(
    F: Ref(Float64),
    G: Ref(Float64),
    H: Ref(Float64),
    SSMIN: Ref(Float64),
    SSMAX: Ref(Float64)
) -> None: ...

@bind("DLASCL")
@external
def dlascl(
    TYPE: Ref(Const(String[1])),
    KL: Ref(Int32),
    KU: Ref(Int32),
    CFROM: Ref(Float64),
    CTO: Ref(Float64),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASCL2")
@external
def dlascl2(
    M: Ref(Int32),
    N: Ref(Int32),
    D: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Ref(Int32)
) -> None: ...

@bind("DLASD0")
@external
def dlasd0(
    N: Ref(Int32),
    SQRE: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ref(Int32),
    SMLSIZ: Ref(Int32),
    IWORK: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASD1")
@external
def dlasd1(
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    D: Float64[Flat],
    ALPHA: Ref(Float64),
    BETA: Ref(Float64),
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ref(Int32),
    IDXQ: Int32[Flat],
    IWORK: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASD2")
@external
def dlasd2(
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    K: Ref(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    ALPHA: Ref(Float64),
    BETA: Ref(Float64),
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ref(Int32),
    DSIGMA: Float64[Flat],
    U2: Float64[LDU2, Flat],
    LDU2: Ref(Int32),
    VT2: Float64[LDVT2, Flat],
    LDVT2: Ref(Int32),
    IDXP: Int32[Flat],
    IDX: Int32[Flat],
    IDXC: Int32[Flat],
    IDXQ: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASD3")
@external
def dlasd3(
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    K: Ref(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    DSIGMA: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Ref(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ref(Int32),
    VT2: Float64[LDVT2, Flat],
    LDVT2: Ref(Int32),
    IDXC: Int32[Flat],
    CTOT: Int32[Flat],
    Z: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASD4")
@external
def dlasd4(
    N: Ref(Int32),
    I: Ref(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    DELTA: Float64[Flat],
    RHO: Ref(Float64),
    SIGMA: Ref(Float64),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASD5")
@external
def dlasd5(
    I: Ref(Int32),
    D: Float64[2],
    Z: Float64[2],
    DELTA: Float64[2],
    RHO: Ref(Float64),
    DSIGMA: Ref(Float64),
    WORK: Float64[2]
) -> None: ...

@bind("DLASD6")
@external
def dlasd6(
    ICOMPQ: Ref(Int32),
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    D: Float64[Flat],
    VF: Float64[Flat],
    VL: Float64[Flat],
    ALPHA: Ref(Float64),
    BETA: Ref(Float64),
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Ref(Int32),
    POLES: Float64[LDGNUM, Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[Flat],
    Z: Float64[Flat],
    K: Ref(Int32),
    C: Ref(Float64),
    S: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASD7")
@external
def dlasd7(
    ICOMPQ: Ref(Int32),
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    K: Ref(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    ZW: Float64[Flat],
    VF: Float64[Flat],
    VFW: Float64[Flat],
    VL: Float64[Flat],
    VLW: Float64[Flat],
    ALPHA: Ref(Float64),
    BETA: Ref(Float64),
    DSIGMA: Float64[Flat],
    IDX: Int32[Flat],
    IDXP: Int32[Flat],
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Ref(Int32),
    C: Ref(Float64),
    S: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASD8")
@external
def dlasd8(
    ICOMPQ: Ref(Int32),
    K: Ref(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    VF: Float64[Flat],
    VL: Float64[Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[LDDIFR, Flat],
    LDDIFR: Ref(Int32),
    DSIGMA: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASDA")
@external
def dlasda(
    ICOMPQ: Ref(Int32),
    SMLSIZ: Ref(Int32),
    N: Ref(Int32),
    SQRE: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float64[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float64[LDU, Flat],
    DIFR: Float64[LDU, Flat],
    Z: Float64[LDU, Flat],
    POLES: Float64[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float64[LDU, Flat],
    C: Float64[Flat],
    S: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASDQ")
@external
def dlasdq(
    UPLO: Ref(Const(String[1])),
    SQRE: Ref(Int32),
    N: Ref(Int32),
    NCVT: Ref(Int32),
    NRU: Ref(Int32),
    NCC: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VT: Float64[LDVT, Flat],
    LDVT: Ref(Int32),
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASDT")
@external
def dlasdt(
    N: Ref(Int32),
    LVL: Ref(Int32),
    ND: Ref(Int32),
    INODE: Int32[Flat],
    NDIML: Int32[Flat],
    NDIMR: Int32[Flat],
    MSUB: Ref(Int32)
) -> None: ...

@bind("DLASET")
@external
def dlaset(
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    BETA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("DLASQ1")
@external
def dlasq1(
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASQ2")
@external
def dlasq2(
    N: Ref(Int32),
    Z: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASQ3")
@external
def dlasq3(
    I0: Ref(Int32),
    N0: Ref(Int32),
    Z: Float64[Flat],
    PP: Ref(Int32),
    DMIN: Ref(Float64),
    SIGMA: Ref(Float64),
    DESIG: Ref(Float64),
    QMAX: Ref(Float64),
    NFAIL: Ref(Int32),
    ITER: Ref(Int32),
    NDIV: Ref(Int32),
    IEEE: Ref(Bool),
    TTYPE: Ref(Int32),
    DMIN1: Ref(Float64),
    DMIN2: Ref(Float64),
    DN: Ref(Float64),
    DN1: Ref(Float64),
    DN2: Ref(Float64),
    G: Ref(Float64),
    TAU: Ref(Float64)
) -> None: ...

@bind("DLASQ4")
@external
def dlasq4(
    I0: Ref(Int32),
    N0: Ref(Int32),
    Z: Float64[Flat],
    PP: Ref(Int32),
    N0IN: Ref(Int32),
    DMIN: Ref(Float64),
    DMIN1: Ref(Float64),
    DMIN2: Ref(Float64),
    DN: Ref(Float64),
    DN1: Ref(Float64),
    DN2: Ref(Float64),
    TAU: Ref(Float64),
    TTYPE: Ref(Int32),
    G: Ref(Float64)
) -> None: ...

@bind("DLASQ5")
@external
def dlasq5(
    I0: Ref(Int32),
    N0: Ref(Int32),
    Z: Float64[Flat],
    PP: Ref(Int32),
    TAU: Ref(Float64),
    SIGMA: Ref(Float64),
    DMIN: Ref(Float64),
    DMIN1: Ref(Float64),
    DMIN2: Ref(Float64),
    DN: Ref(Float64),
    DNM1: Ref(Float64),
    DNM2: Ref(Float64),
    IEEE: Ref(Bool),
    EPS: Ref(Float64)
) -> None: ...

@bind("DLASQ6")
@external
def dlasq6(
    I0: Ref(Int32),
    N0: Ref(Int32),
    Z: Float64[Flat],
    PP: Ref(Int32),
    DMIN: Ref(Float64),
    DMIN1: Ref(Float64),
    DMIN2: Ref(Float64),
    DN: Ref(Float64),
    DNM1: Ref(Float64),
    DNM2: Ref(Float64)
) -> None: ...

@bind("DLASR")
@external
def dlasr(
    SIDE: Ref(Const(String[1])),
    PIVOT: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    A: Float64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("DLASRT")
@external
def dlasrt(
    ID: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASSQ")
@external
def dlassq(
    n: Ref(Int32),
    x: Float64[Flat],
    incx: Ref(Int32),
    scale: Ref(Float64),
    sumsq: Ref(Float64)
) -> None: ...

@bind("DLASV2")
@external
def dlasv2(
    F: Ref(Float64),
    G: Ref(Float64),
    H: Ref(Float64),
    SSMIN: Ref(Float64),
    SSMAX: Ref(Float64),
    SNR: Ref(Float64),
    CSR: Ref(Float64),
    SNL: Ref(Float64),
    CSL: Ref(Float64)
) -> None: ...

@bind("DLASWLQ")
@external
def dlaswlq(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASWP")
@external
def dlaswp(
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    K1: Ref(Int32),
    K2: Ref(Int32),
    IPIV: Int32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("DLASY2")
@external
def dlasy2(
    LTRANL: Ref(Bool),
    LTRANR: Ref(Bool),
    ISGN: Ref(Int32),
    N1: Ref(Int32),
    N2: Ref(Int32),
    TL: Float64[LDTL, Flat],
    LDTL: Ref(Int32),
    TR: Float64[LDTR, Flat],
    LDTR: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    SCALE: Ref(Float64),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    XNORM: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASYF")
@external
def dlasyf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Float64[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASYF_AA")
@external
def dlasyf_aa(
    UPLO: Ref(Const(String[1])),
    J1: Ref(Int32),
    M: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    H: Float64[LDH, Flat],
    LDH: Ref(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLASYF_RK")
@external
def dlasyf_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    W: Float64[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLASYF_ROOK")
@external
def dlasyf_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Float64[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAT2S")
@external
def dlat2s(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    SA: Float32[LDSA, Flat],
    LDSA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLATBS")
@external
def dlatbs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    X: Float64[Flat],
    SCALE: Ref(Float64),
    CNORM: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLATDF")
@external
def dlatdf(
    IJOB: Ref(Int32),
    N: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    RHS: Float64[Flat],
    RDSUM: Ref(Float64),
    RDSCAL: Ref(Float64),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("DLATPS")
@external
def dlatps(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    X: Float64[Flat],
    SCALE: Ref(Float64),
    CNORM: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLATRD")
@external
def dlatrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    TAU: Float64[Flat],
    W: Float64[LDW, Flat],
    LDW: Ref(Int32)
) -> None: ...

@bind("DLATRS")
@external
def dlatrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    X: Float64[Flat],
    SCALE: Ref(Float64),
    CNORM: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DLATRS3")
@external
def dlatrs3(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    SCALE: Float64[Flat],
    CNORM: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLATRZ")
@external
def dlatrz(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat]
) -> None: ...

@bind("DLATSQR")
@external
def dlatsqr(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAUU2")
@external
def dlauu2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DLAUUM")
@external
def dlauum(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DOPGTR")
@external
def dopgtr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    TAU: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DOPMTR")
@external
def dopmtr(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    AP: Float64[Flat],
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORBDB")
@external
def dorbdb(
    TRANS: Ref(Const(String[1])),
    SIGNS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ref(Int32),
    X12: Float64[LDX12, Flat],
    LDX12: Ref(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ref(Int32),
    X22: Float64[LDX22, Flat],
    LDX22: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    TAUQ2: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORBDB1")
@external
def dorbdb1(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORBDB2")
@external
def dorbdb2(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORBDB3")
@external
def dorbdb3(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORBDB4")
@external
def dorbdb4(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    PHANTOM: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORBDB5")
@external
def dorbdb5(
    M1: Ref(Int32),
    M2: Ref(Int32),
    N: Ref(Int32),
    X1: Float64[Flat],
    INCX1: Ref(Int32),
    X2: Float64[Flat],
    INCX2: Ref(Int32),
    Q1: Float64[LDQ1, Flat],
    LDQ1: Ref(Int32),
    Q2: Float64[LDQ2, Flat],
    LDQ2: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORBDB6")
@external
def dorbdb6(
    M1: Ref(Int32),
    M2: Ref(Int32),
    N: Ref(Int32),
    X1: Float64[Flat],
    INCX1: Ref(Int32),
    X2: Float64[Flat],
    INCX2: Ref(Int32),
    Q1: Float64[LDQ1, Flat],
    LDQ1: Ref(Int32),
    Q2: Float64[LDQ2, Flat],
    LDQ2: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORCSD")
@external
def dorcsd(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    JOBV2T: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    SIGNS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ref(Int32),
    X12: Float64[LDX12, Flat],
    LDX12: Ref(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ref(Int32),
    X22: Float64[LDX22, Flat],
    LDX22: Ref(Int32),
    THETA: Float64[Flat],
    U1: Float64[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Float64[LDV1T, Flat],
    LDV1T: Ref(Int32),
    V2T: Float64[LDV2T, Flat],
    LDV2T: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORCSD2BY1")
@external
def dorcsd2by1(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float64[Flat],
    U1: Float64[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Float64[LDV1T, Flat],
    LDV1T: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORG2L")
@external
def dorg2l(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORG2R")
@external
def dorg2r(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGBR")
@external
def dorgbr(
    VECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGHR")
@external
def dorghr(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGL2")
@external
def dorgl2(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGLQ")
@external
def dorglq(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGQL")
@external
def dorgql(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGQR")
@external
def dorgqr(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGR2")
@external
def dorgr2(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGRQ")
@external
def dorgrq(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGTR")
@external
def dorgtr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGTSQR")
@external
def dorgtsqr(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORGTSQR_ROW")
@external
def dorgtsqr_row(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORHR_COL")
@external
def dorhr_col(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    D: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORM22")
@external
def dorm22(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    N2: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORM2L")
@external
def dorm2l(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORM2R")
@external
def dorm2r(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORMBR")
@external
def dormbr(
    VECT: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORMHR")
@external
def dormhr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORML2")
@external
def dorml2(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORMLQ")
@external
def dormlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORMQL")
@external
def dormql(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORMQR")
@external
def dormqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORMR2")
@external
def dormr2(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORMR3")
@external
def dormr3(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DORMRQ")
@external
def dormrq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORMRZ")
@external
def dormrz(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DORMTR")
@external
def dormtr(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPBCON")
@external
def dpbcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPBEQU")
@external
def dpbequ(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPBRFS")
@external
def dpbrfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPBSTF")
@external
def dpbstf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPBSV")
@external
def dpbsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPBSVX")
@external
def dpbsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPBTF2")
@external
def dpbtf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPBTRF")
@external
def dpbtrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPBTRS")
@external
def dpbtrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPFTRF")
@external
def dpftrf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPFTRI")
@external
def dpftri(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPFTRS")
@external
def dpftrs(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOCON")
@external
def dpocon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOEQU")
@external
def dpoequ(
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOEQUB")
@external
def dpoequb(
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPORFS")
@external
def dporfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPORFSX")
@external
def dporfsx(
    UPLO: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOSV")
@external
def dposv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOSVX")
@external
def dposvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOSVXX")
@external
def dposvxx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    RPVGRW: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOTF2")
@external
def dpotf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOTRF")
@external
def dpotrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOTRF2")
@external
def dpotrf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOTRI")
@external
def dpotri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPOTRS")
@external
def dpotrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPPCON")
@external
def dppcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPPEQU")
@external
def dppequ(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPPRFS")
@external
def dpprfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPPSV")
@external
def dppsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPPSVX")
@external
def dppsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPPTRF")
@external
def dpptrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPPTRI")
@external
def dpptri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPPTRS")
@external
def dpptrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPSTF2")
@external
def dpstf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    PIV: Int32[N],
    RANK: Ref(Int32),
    TOL: Ref(Float64),
    WORK: Float64[2 * N],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPSTRF")
@external
def dpstrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    PIV: Int32[N],
    RANK: Ref(Int32),
    TOL: Ref(Float64),
    WORK: Float64[2 * N],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPTCON")
@external
def dptcon(
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPTEQR")
@external
def dpteqr(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPTRFS")
@external
def dptrfs(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    DF: Float64[Flat],
    EF: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPTSV")
@external
def dptsv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPTSVX")
@external
def dptsvx(
    FACT: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    DF: Float64[Flat],
    EF: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPTTRF")
@external
def dpttrf(
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DPTTRS")
@external
def dpttrs(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DPTTS2")
@external
def dptts2(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("DRSCL")
@external
def drscl(
    N: Ref(Int32),
    SA: Ref(Float64),
    SX: Float64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("DSB2ST_KERNELS")
@external
def dsb2st_kernels(
    UPLO: Ref(Const(String[1])),
    WANTZ: Ref(Bool),
    TTYPE: Ref(Int32),
    ST: Ref(Int32),
    ED: Ref(Int32),
    SWEEP: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    IB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    V: Float64[Flat],
    TAU: Float64[Flat],
    LDVT: Ref(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DSBEV")
@external
def dsbev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSBEV_2STAGE")
@external
def dsbev_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSBEVD")
@external
def dsbevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSBEVD_2STAGE")
@external
def dsbevd_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSBEVX")
@external
def dsbevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSBEVX_2STAGE")
@external
def dsbevx_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSBGST")
@external
def dsbgst(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSBGV")
@external
def dsbgv(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSBGVD")
@external
def dsbgvd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSBGVX")
@external
def dsbgvx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSBTRD")
@external
def dsbtrd(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSFRK")
@external
def dsfrk(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    BETA: Ref(Float64),
    C: Float64[Flat]
) -> None: ...

@bind("DSGESV")
@external
def dsgesv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    WORK: Float64[N, Flat],
    SWORK: Float32[Flat],
    ITER: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPCON")
@external
def dspcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPEV")
@external
def dspev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPEVD")
@external
def dspevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPEVX")
@external
def dspevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPGST")
@external
def dspgst(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPGV")
@external
def dspgv(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPGVD")
@external
def dspgvd(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPGVX")
@external
def dspgvx(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPOSV")
@external
def dsposv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    WORK: Float64[N, Flat],
    SWORK: Float32[Flat],
    ITER: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPRFS")
@external
def dsprfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPSV")
@external
def dspsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPSVX")
@external
def dspsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPTRD")
@external
def dsptrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPTRF")
@external
def dsptrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPTRI")
@external
def dsptri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSPTRS")
@external
def dsptrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTEBZ")
@external
def dstebz(
    RANGE: Ref(Const(String[1])),
    ORDER: Ref(Const(String[1])),
    N: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    M: Ref(Int32),
    NSPLIT: Ref(Int32),
    W: Float64[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTEDC")
@external
def dstedc(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTEGR")
@external
def dstegr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTEIN")
@external
def dstein(
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    M: Ref(Int32),
    W: Float64[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTEMR")
@external
def dstemr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    NZC: Ref(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Ref(Bool),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTEQR")
@external
def dsteqr(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTERF")
@external
def dsterf(
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTEV")
@external
def dstev(
    JOBZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTEVD")
@external
def dstevd(
    JOBZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTEVR")
@external
def dstevr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSTEVX")
@external
def dstevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYCON")
@external
def dsycon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYCON_3")
@external
def dsycon_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYCON_ROOK")
@external
def dsycon_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYCONV")
@external
def dsyconv(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    E: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYCONVF")
@external
def dsyconvf(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYCONVF_ROOK")
@external
def dsyconvf_rook(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYEQUB")
@external
def dsyequb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYEV")
@external
def dsyev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYEV_2STAGE")
@external
def dsyev_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYEVD")
@external
def dsyevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYEVD_2STAGE")
@external
def dsyevd_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYEVR")
@external
def dsyevr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYEVR_2STAGE")
@external
def dsyevr_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYEVX")
@external
def dsyevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYEVX_2STAGE")
@external
def dsyevx_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYGS2")
@external
def dsygs2(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYGST")
@external
def dsygst(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYGV")
@external
def dsygv(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYGV_2STAGE")
@external
def dsygv_2stage(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYGVD")
@external
def dsygvd(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYGVX")
@external
def dsygvx(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYRFS")
@external
def dsyrfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYRFSX")
@external
def dsyrfsx(
    UPLO: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYSV")
@external
def dsysv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYSV_AA")
@external
def dsysv_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYSV_AA_2STAGE")
@external
def dsysv_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TB: Float64[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYSV_RK")
@external
def dsysv_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYSV_ROOK")
@external
def dsysv_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYSVX")
@external
def dsysvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYSVXX")
@external
def dsysvxx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    RPVGRW: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYSWAPR")
@external
def dsyswapr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    I1: Ref(Int32),
    I2: Ref(Int32)
) -> None: ...

@bind("DSYTD2")
@external
def dsytd2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTF2")
@external
def dsytf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTF2_RK")
@external
def dsytf2_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTF2_ROOK")
@external
def dsytf2_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRD")
@external
def dsytrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRD_2STAGE")
@external
def dsytrd_2stage(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    HOUS2: Float64[Flat],
    LHOUS2: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRD_SB2ST")
@external
def dsytrd_sb2st(
    STAGE1: Ref(Const(String[1])),
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    HOUS: Float64[Flat],
    LHOUS: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRD_SY2SB")
@external
def dsytrd_sy2sb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRF")
@external
def dsytrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRF_AA")
@external
def dsytrf_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRF_AA_2STAGE")
@external
def dsytrf_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TB: Float64[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRF_RK")
@external
def dsytrf_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRF_ROOK")
@external
def dsytrf_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRI")
@external
def dsytri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRI2")
@external
def dsytri2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRI2X")
@external
def dsytri2x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRI_3")
@external
def dsytri_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRI_3X")
@external
def dsytri_3x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRI_ROOK")
@external
def dsytri_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRS")
@external
def dsytrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRS2")
@external
def dsytrs2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRS_3")
@external
def dsytrs_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRS_AA")
@external
def dsytrs_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRS_AA_2STAGE")
@external
def dsytrs_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TB: Float64[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DSYTRS_ROOK")
@external
def dsytrs_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTBCON")
@external
def dtbcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTBRFS")
@external
def dtbrfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTBTRS")
@external
def dtbtrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTFSM")
@external
def dtfsm(
    TRANSR: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    B: Annotated[Float64[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Ref(Int32)
) -> None: ...

@bind("DTFTRI")
@external
def dtftri(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTFTTP")
@external
def dtfttp(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    AP: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTFTTR")
@external
def dtfttr(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    A: Annotated[Float64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTGEVC")
@external
def dtgevc(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    S: Float64[LDS, Flat],
    LDS: Ref(Int32),
    P: Float64[LDP, Flat],
    LDP: Ref(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTGEX2")
@external
def dtgex2(
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    J1: Ref(Int32),
    N1: Ref(Int32),
    N2: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTGEXC")
@external
def dtgexc(
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    IFST: Ref(Int32),
    ILST: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTGSEN")
@external
def dtgsen(
    IJOB: Ref(Int32),
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ref(Int32),
    M: Ref(Int32),
    PL: Ref(Float64),
    PR: Ref(Float64),
    DIF: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTGSJA")
@external
def dtgsja(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    TOLA: Ref(Float64),
    TOLB: Ref(Float64),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Float64[Flat],
    NCYCLE: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTGSNA")
@external
def dtgsna(
    JOB: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    S: Float64[Flat],
    DIF: Float64[Flat],
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTGSY2")
@external
def dtgsy2(
    TRANS: Ref(Const(String[1])),
    IJOB: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    D: Float64[LDD, Flat],
    LDD: Ref(Int32),
    E: Float64[LDE, Flat],
    LDE: Ref(Int32),
    F: Float64[LDF, Flat],
    LDF: Ref(Int32),
    SCALE: Ref(Float64),
    RDSUM: Ref(Float64),
    RDSCAL: Ref(Float64),
    IWORK: Int32[Flat],
    PQ: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTGSYL")
@external
def dtgsyl(
    TRANS: Ref(Const(String[1])),
    IJOB: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    D: Float64[LDD, Flat],
    LDD: Ref(Int32),
    E: Float64[LDE, Flat],
    LDE: Ref(Int32),
    F: Float64[LDF, Flat],
    LDF: Ref(Int32),
    SCALE: Ref(Float64),
    DIF: Ref(Float64),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPCON")
@external
def dtpcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPLQT")
@external
def dtplqt(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    MB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPLQT2")
@external
def dtplqt2(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPMLQT")
@external
def dtpmlqt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    MB: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPMQRT")
@external
def dtpmqrt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    NB: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPQRT")
@external
def dtpqrt(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    NB: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPQRT2")
@external
def dtpqrt2(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPRFB")
@external
def dtprfb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    V: Float64[LDV, Flat],
    LDV: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("DTPRFS")
@external
def dtprfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPTRI")
@external
def dtptri(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPTRS")
@external
def dtptrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPTTF")
@external
def dtpttf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Annotated[Float64[Flat], SourceDims("0:*")],
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTPTTR")
@external
def dtpttr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRCON")
@external
def dtrcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    RCOND: Ref(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTREVC")
@external
def dtrevc(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTREVC3")
@external
def dtrevc3(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTREXC")
@external
def dtrexc(
    COMPQ: Ref(Const(String[1])),
    N: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    IFST: Ref(Int32),
    ILST: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRRFS")
@external
def dtrrfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    X: Float64[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRSEN")
@external
def dtrsen(
    JOB: Ref(Const(String[1])),
    COMPQ: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ref(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    M: Ref(Int32),
    S: Ref(Float64),
    SEP: Ref(Float64),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRSNA")
@external
def dtrsna(
    JOB: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Float64[LDT, Flat],
    LDT: Ref(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ref(Int32),
    S: Float64[Flat],
    SEP: Float64[Flat],
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRSYL")
@external
def dtrsyl(
    TRANA: Ref(Const(String[1])),
    TRANB: Ref(Const(String[1])),
    ISGN: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    SCALE: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRSYL3")
@external
def dtrsyl3(
    TRANA: Ref(Const(String[1])),
    TRANB: Ref(Const(String[1])),
    ISGN: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32),
    SCALE: Ref(Float64),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    SWORK: Float64[LDSWORK, Flat],
    LDSWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRTI2")
@external
def dtrti2(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRTRI")
@external
def dtrtri(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRTRS")
@external
def dtrtrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRTTF")
@external
def dtrttf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Float64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ref(Int32),
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTRTTP")
@external
def dtrttp(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    AP: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("DTZRZF")
@external
def dtzrzf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("DZSUM1")
@external
def dzsum1(
    N: Ref(Int32),
    CX: Complex128[Flat],
    INCX: Ref(Int32)
) -> Float64: ...

@bind("ICMAX1")
@external
def icmax1(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32)
) -> Int32: ...

@bind("IEEECK")
@external
def ieeeck(
    ISPEC: Ref(Int32),
    ZERO: Ref(Float32),
    ONE: Ref(Float32)
) -> Int32: ...

@bind("ILACLC")
@external
def ilaclc(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32)
) -> Int32: ...

@bind("ILACLR")
@external
def ilaclr(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32)
) -> Int32: ...

@bind("ILADIAG")
@external
def iladiag(
    DIAG: Ref(Const(String[1]))
) -> Int32: ...

@bind("ILADLC")
@external
def iladlc(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32)
) -> Int32: ...

@bind("ILADLR")
@external
def iladlr(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32)
) -> Int32: ...

@bind("ILAENV")
@external
def ilaenv(
    ISPEC: Ref(Int32),
    NAME: Ref(Const(String)),
    OPTS: Ref(Const(String)),
    N1: Ref(Int32),
    N2: Ref(Int32),
    N3: Ref(Int32),
    N4: Ref(Int32)
) -> Int32: ...

@bind("ILAENV2STAGE")
@external
def ilaenv2stage(
    ISPEC: Ref(Int32),
    NAME: Ref(Const(String)),
    OPTS: Ref(Const(String)),
    N1: Ref(Int32),
    N2: Ref(Int32),
    N3: Ref(Int32),
    N4: Ref(Int32)
) -> Int32: ...

@bind("ILAPREC")
@external
def ilaprec(
    PREC: Ref(Const(String[1]))
) -> Int32: ...

@bind("ILASLC")
@external
def ilaslc(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32)
) -> Int32: ...

@bind("ILASLR")
@external
def ilaslr(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32)
) -> Int32: ...

@bind("ILATRANS")
@external
def ilatrans(
    TRANS: Ref(Const(String[1]))
) -> Int32: ...

@bind("ILAUPLO")
@external
def ilauplo(
    UPLO: Ref(Const(String[1]))
) -> Int32: ...

@bind("ILAZLC")
@external
def ilazlc(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32)
) -> Int32: ...

@bind("ILAZLR")
@external
def ilazlr(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32)
) -> Int32: ...

@bind("IPARAM2STAGE")
@external
def iparam2stage(
    ISPEC: Ref(Int32),
    NAME: Ref(Const(String)),
    OPTS: Ref(Const(String)),
    NI: Ref(Int32),
    NBI: Ref(Int32),
    IBI: Ref(Int32),
    NXI: Ref(Int32)
) -> Int32: ...

@bind("IPARMQ")
@external
def iparmq(
    ISPEC: Ref(Int32),
    NAME: String[1][Flat],
    OPTS: String[1][Flat],
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LWORK: Ref(Int32)
) -> Int32: ...

@bind("IZMAX1")
@external
def izmax1(
    N: Ref(Int32),
    ZX: Complex128[Flat],
    INCX: Ref(Int32)
) -> Int32: ...

@bind("LSAMEN")
@external
def lsamen(
    N: Ref(Int32),
    CA: Ref(Const(String)),
    CB: Ref(Const(String))
) -> Bool: ...

@bind("SBBCSD")
@external
def sbbcsd(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    JOBV2T: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    U1: Float32[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Float32[LDV1T, Flat],
    LDV1T: Ref(Int32),
    V2T: Float32[LDV2T, Flat],
    LDV2T: Ref(Int32),
    B11D: Float32[Flat],
    B11E: Float32[Flat],
    B12D: Float32[Flat],
    B12E: Float32[Flat],
    B21D: Float32[Flat],
    B21E: Float32[Flat],
    B22D: Float32[Flat],
    B22E: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SBDSDC")
@external
def sbdsdc(
    UPLO: Ref(Const(String[1])),
    COMPQ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ref(Int32),
    Q: Float32[Flat],
    IQ: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SBDSQR")
@external
def sbdsqr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NCVT: Ref(Int32),
    NRU: Ref(Int32),
    NCC: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VT: Float32[LDVT, Flat],
    LDVT: Ref(Int32),
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SBDSVDX")
@external
def sbdsvdx(
    UPLO: Ref(Const(String[1])),
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    NS: Ref(Int32),
    S: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SCSUM1")
@external
def scsum1(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32)
) -> Float32: ...

@bind("SDISNA")
@external
def sdisna(
    JOB: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    D: Float32[Flat],
    SEP: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBBRD")
@external
def sgbbrd(
    VECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NCC: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    PT: Float32[LDPT, Flat],
    LDPT: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBCON")
@external
def sgbcon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBEQU")
@external
def sgbequ(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBEQUB")
@external
def sgbequb(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBRFS")
@external
def sgbrfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBRFSX")
@external
def sgbrfsx(
    TRANS: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBSV")
@external
def sgbsv(
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBSVX")
@external
def sgbsvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBSVXX")
@external
def sgbsvxx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    RPVGRW: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBTF2")
@external
def sgbtf2(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBTRF")
@external
def sgbtrf(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGBTRS")
@external
def sgbtrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEBAK")
@external
def sgebak(
    JOB: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float32[Flat],
    M: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEBAL")
@external
def sgebal(
    JOB: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEBD2")
@external
def sgebd2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Float32[Flat],
    TAUP: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEBRD")
@external
def sgebrd(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Float32[Flat],
    TAUP: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGECON")
@external
def sgecon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Arg(7), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Ref(Arg(11)), Ref(Arg(12)), Return('K', 0), Arg(13), Arg(14), Arg(15), Ref(Arg(16)), Arg(17), Arg(18), Ref(Arg(19)), Arg(20), Ref(Arg(21)), Arg(22), Ref(Arg(23)), Arg(24), Ref(Arg(25)), Arg(26), Ref(Arg(27)), Return('INFO', 10)])
def sgedmd(
    JOBS: Ref(Const(String[1])),
    JOBZ: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBF: Ref(Const(String[1])),
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
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Ref(Arg(6)), Ref(Arg(7)), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Arg(11), Ref(Arg(12)), Arg(13), Ref(Arg(14)), Ref(Arg(15)), Ref(Arg(16)), Return('K', 2), Arg(17), Arg(18), Arg(19), Ref(Arg(20)), Arg(21), Arg(22), Ref(Arg(23)), Arg(24), Ref(Arg(25)), Arg(26), Ref(Arg(27)), Arg(28), Ref(Arg(29)), Arg(30), Ref(Arg(31)), Return('INFO', 12)])
def sgedmdq(
    JOBS: Ref(Const(String[1])),
    JOBZ: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    JOBT: Ref(Const(String[1])),
    JOBF: Ref(Const(String[1])),
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
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEEQUB")
@external
def sgeequb(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEES")
@external
def sgees(
    JOBVS: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELECT: Ref(Bool),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    SDIM: Ref(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VS: Float32[LDVS, Flat],
    LDVS: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEESX")
@external
def sgeesx(
    JOBVS: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELECT: Ref(Bool),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    SDIM: Ref(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VS: Float32[LDVS, Flat],
    LDVS: Ref(Int32),
    RCONDE: Ref(Float32),
    RCONDV: Ref(Float32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEEV")
@external
def sgeev(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEEVX")
@external
def sgeevx(
    BALANC: Ref(Const(String[1])),
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float32[Flat],
    ABNRM: Ref(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEHD2")
@external
def sgehd2(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEHRD")
@external
def sgehrd(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEJSV")
@external
def sgejsv(
    JOBA: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBT: Ref(Const(String[1])),
    JOBP: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    SVA: Float32[N],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    WORK: Float32[LWORK],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGELQ")
@external
def sgelq(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[Flat],
    TSIZE: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGELQ2")
@external
def sgelq2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGELQF")
@external
def sgelqf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGELQT")
@external
def sgelqt(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGELQT3")
@external
def sgelqt3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGELS")
@external
def sgels(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGELSD")
@external
def sgelsd(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    S: Float32[Flat],
    RCOND: Ref(Float32),
    RANK: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGELSS")
@external
def sgelss(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    S: Float32[Flat],
    RCOND: Ref(Float32),
    RANK: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGELST")
@external
def sgelst(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGELSY")
@external
def sgelsy(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    JPVT: Int32[Flat],
    RCOND: Ref(Float32),
    RANK: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEMLQ")
@external
def sgemlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[Flat],
    TSIZE: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEMLQT")
@external
def sgemlqt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEMQR")
@external
def sgemqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[Flat],
    TSIZE: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEMQRT")
@external
def sgemqrt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    NB: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQL2")
@external
def sgeql2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQLF")
@external
def sgeqlf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQP3")
@external
def sgeqp3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQP3RK")
@external
def sgeqp3rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    KMAX: Ref(Int32),
    ABSTOL: Ref(Float32),
    RELTOL: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    K: Ref(Int32),
    MAXC2NRMK: Ref(Float32),
    RELMAXC2NRMK: Ref(Float32),
    JPIV: Int32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQR")
@external
def sgeqr(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[Flat],
    TSIZE: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQR2")
@external
def sgeqr2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQR2P")
@external
def sgeqr2p(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQRF")
@external
def sgeqrf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQRFP")
@external
def sgeqrfp(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQRT")
@external
def sgeqrt(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQRT2")
@external
def sgeqrt2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGEQRT3")
@external
def sgeqrt3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGERFS")
@external
def sgerfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGERFSX")
@external
def sgerfsx(
    TRANS: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGERQ2")
@external
def sgerq2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGERQF")
@external
def sgerqf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGESC2")
@external
def sgesc2(
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    RHS: Float32[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Ref(Float32)
) -> None: ...

@bind("SGESDD")
@external
def sgesdd(
    JOBZ: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGESV")
@external
def sgesv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGESVD")
@external
def sgesvd(
    JOBU: Ref(Const(String[1])),
    JOBVT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGESVDQ")
@external
def sgesvdq(
    JOBA: Ref(Const(String[1])),
    JOBP: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    NUMRANK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGESVDX")
@external
def sgesvdx(
    JOBU: Ref(Const(String[1])),
    JOBVT: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    NS: Ref(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGESVJ")
@external
def sgesvj(
    JOBA: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    SVA: Float32[N],
    MV: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    WORK: Float32[LWORK],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGESVX")
@external
def sgesvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGESVXX")
@external
def sgesvxx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    RPVGRW: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGETC2")
@external
def sgetc2(
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGETF2")
@external
def sgetf2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGETRF")
@external
def sgetrf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGETRF2")
@external
def sgetrf2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGETRI")
@external
def sgetri(
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGETRS")
@external
def sgetrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGETSLS")
@external
def sgetsls(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGETSQRHRT")
@external
def sgetsqrhrt(
    M: Ref(Int32),
    N: Ref(Int32),
    MB1: Ref(Int32),
    NB1: Ref(Int32),
    NB2: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGBAK")
@external
def sggbak(
    JOB: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    M: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGBAL")
@external
def sggbal(
    JOB: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGES")
@external
def sgges(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VSL: Float32[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Float32[LDVSR, Flat],
    LDVSR: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGES3")
@external
def sgges3(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VSL: Float32[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Float32[LDVSR, Flat],
    LDVSR: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGESX")
@external
def sggesx(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VSL: Float32[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Float32[LDVSR, Flat],
    LDVSR: Ref(Int32),
    RCONDE: Float32[2],
    RCONDV: Float32[2],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGEV")
@external
def sggev(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGEV3")
@external
def sggev3(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGEVX")
@external
def sggevx(
    BALANC: Ref(Const(String[1])),
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    ABNRM: Ref(Float32),
    BBNRM: Ref(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGGLM")
@external
def sggglm(
    N: Ref(Int32),
    M: Ref(Int32),
    P: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    D: Float32[Flat],
    X: Float32[Flat],
    Y: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGHD3")
@external
def sgghd3(
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGHRD")
@external
def sgghrd(
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGLSE")
@external
def sgglse(
    M: Ref(Int32),
    N: Ref(Int32),
    P: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    C: Float32[Flat],
    D: Float32[Flat],
    X: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGQRF")
@external
def sggqrf(
    N: Ref(Int32),
    M: Ref(Int32),
    P: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAUA: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    TAUB: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGRQF")
@external
def sggrqf(
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAUA: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    TAUB: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGSVD3")
@external
def sggsvd3(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    P: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGGSVP3")
@external
def sggsvp3(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    TOLA: Ref(Float32),
    TOLB: Ref(Float32),
    K: Ref(Int32),
    L: Ref(Int32),
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    IWORK: Int32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGSVJ0")
@external
def sgsvj0(
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[N],
    SVA: Float32[N],
    MV: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    EPS: Ref(Float32),
    SFMIN: Ref(Float32),
    TOL: Ref(Float32),
    NSWEEP: Ref(Int32),
    WORK: Float32[LWORK],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGSVJ1")
@external
def sgsvj1(
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[N],
    SVA: Float32[N],
    MV: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    EPS: Ref(Float32),
    SFMIN: Ref(Float32),
    TOL: Ref(Float32),
    NSWEEP: Ref(Int32),
    WORK: Float32[LWORK],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGTCON")
@external
def sgtcon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGTRFS")
@external
def sgtrfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DLF: Float32[Flat],
    DF: Float32[Flat],
    DUF: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGTSV")
@external
def sgtsv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGTSVX")
@external
def sgtsvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DLF: Float32[Flat],
    DF: Float32[Flat],
    DUF: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGTTRF")
@external
def sgttrf(
    N: Ref(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SGTTRS")
@external
def sgttrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SGTTS2")
@external
def sgtts2(
    ITRANS: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("SHGEQZ")
@external
def shgeqz(
    JOB: Ref(Const(String[1])),
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SHSEIN")
@external
def shsein(
    SIDE: Ref(Const(String[1])),
    EIGSRC: Ref(Const(String[1])),
    INITV: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float32[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SHSEQR")
@external
def shseqr(
    JOB: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SISNAN")
@external
@native_call([Ref(Arg(0))])
def sisnan(
    SIN: Const(Float32)
) -> Bool: ...

@bind("SLA_GBAMV")
@external
def sla_gbamv(
    TRANS: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    ALPHA: Ref(Float32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float32),
    Y: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("SLA_GBRCOND")
@external
def sla_gbrcond(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    CMODE: Ref(Int32),
    C: Float32[Flat],
    INFO: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_GBRFSX_EXTENDED")
@external
def sla_gbrfsx_extended(
    PREC_TYPE: Ref(Int32),
    TRANS_TYPE: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    Y: Float32[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Ref(Float32),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float32),
    DZ_UB: Ref(Float32),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLA_GBRPVGRW")
@external
def sla_gbrpvgrw(
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NCOLS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ref(Int32)
) -> Float32: ...

@bind("SLA_GEAMV")
@external
def sla_geamv(
    TRANS: Ref(Int32),
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

@bind("SLA_GERCOND")
@external
def sla_gercond(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    CMODE: Ref(Int32),
    C: Float32[Flat],
    INFO: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_GERFSX_EXTENDED")
@external
def sla_gerfsx_extended(
    PREC_TYPE: Ref(Int32),
    TRANS_TYPE: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    Y: Float32[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ref(Int32),
    ERRS_N: Float32[NRHS, Flat],
    ERRS_C: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Ref(Float32),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float32),
    DZ_UB: Ref(Float32),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLA_GERPVGRW")
@external
def sla_gerpvgrw(
    N: Ref(Int32),
    NCOLS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32)
) -> Float32: ...

@bind("SLA_LIN_BERR")
@external
def sla_lin_berr(
    N: Ref(Int32),
    NZ: Ref(Int32),
    NRHS: Ref(Int32),
    RES: Annotated[Float32[N, NRHS], ORDER_F],
    AYB: Annotated[Float32[N, NRHS], ORDER_F],
    BERR: Float32[NRHS]
) -> None: ...

@bind("SLA_PORCOND")
@external
def sla_porcond(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    CMODE: Ref(Int32),
    C: Float32[Flat],
    INFO: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_PORFSX_EXTENDED")
@external
def sla_porfsx_extended(
    PREC_TYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    COLEQU: Ref(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    Y: Float32[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Ref(Float32),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float32),
    DZ_UB: Ref(Float32),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLA_PORPVGRW")
@external
def sla_porpvgrw(
    UPLO: Ref(Const(String[1])),
    NCOLS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLA_SYAMV")
@external
def sla_syamv(
    UPLO: Ref(Int32),
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

@bind("SLA_SYRCOND")
@external
def sla_syrcond(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    CMODE: Ref(Int32),
    C: Float32[Flat],
    INFO: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_SYRFSX_EXTENDED")
@external
def sla_syrfsx_extended(
    PREC_TYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    Y: Float32[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Ref(Float32),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float32),
    DZ_UB: Ref(Float32),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLA_SYRPVGRW")
@external
def sla_syrpvgrw(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    INFO: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLA_WWADDW")
@external
def sla_wwaddw(
    N: Ref(Int32),
    X: Float32[Flat],
    Y: Float32[Flat],
    W: Float32[Flat]
) -> None: ...

@bind("SLABAD")
@external
def slabad(
    SMALL: Ref(Float32),
    LARGE: Ref(Float32)
) -> None: ...

@bind("SLABRD")
@external
def slabrd(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Float32[Flat],
    TAUP: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    Y: Float32[LDY, Flat],
    LDY: Ref(Int32)
) -> None: ...

@bind("SLACN2")
@external
def slacn2(
    N: Ref(Int32),
    V: Float32[Flat],
    X: Float32[Flat],
    ISGN: Int32[Flat],
    EST: Ref(Float32),
    KASE: Ref(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("SLACON")
@external
def slacon(
    N: Ref(Int32),
    V: Float32[Flat],
    X: Float32[Flat],
    ISGN: Int32[Flat],
    EST: Ref(Float32),
    KASE: Ref(Int32)
) -> None: ...

@bind("SLACPY")
@external
def slacpy(
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("SLADIV")
@external
def sladiv(
    A: Ref(Float32),
    B: Ref(Float32),
    C: Ref(Float32),
    D: Ref(Float32),
    P: Ref(Float32),
    Q: Ref(Float32)
) -> None: ...

@bind("SLADIV1")
@external
def sladiv1(
    A: Ref(Float32),
    B: Ref(Float32),
    C: Ref(Float32),
    D: Ref(Float32),
    P: Ref(Float32),
    Q: Ref(Float32)
) -> None: ...

@bind("SLADIV2")
@external
def sladiv2(
    A: Ref(Float32),
    B: Ref(Float32),
    C: Ref(Float32),
    D: Ref(Float32),
    R: Ref(Float32),
    T: Ref(Float32)
) -> Float32: ...

@bind("SLAE2")
@external
def slae2(
    A: Ref(Float32),
    B: Ref(Float32),
    C: Ref(Float32),
    RT1: Ref(Float32),
    RT2: Ref(Float32)
) -> None: ...

@bind("SLAEBZ")
@external
def slaebz(
    IJOB: Ref(Int32),
    NITMAX: Ref(Int32),
    N: Ref(Int32),
    MMAX: Ref(Int32),
    MINP: Ref(Int32),
    NBMIN: Ref(Int32),
    ABSTOL: Ref(Float32),
    RELTOL: Ref(Float32),
    PIVMIN: Ref(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    NVAL: Int32[Flat],
    AB: Float32[MMAX, Flat],
    C: Float32[Flat],
    MOUT: Ref(Int32),
    NAB: Int32[MMAX, Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAED0")
@external
def slaed0(
    ICOMPQ: Ref(Int32),
    QSIZ: Ref(Int32),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    QSTORE: Float32[LDQS, Flat],
    LDQS: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAED1")
@external
def slaed1(
    N: Ref(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    INDXQ: Int32[Flat],
    RHO: Ref(Float32),
    CUTPNT: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAED2")
@external
def slaed2(
    K: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    INDXQ: Int32[Flat],
    RHO: Ref(Float32),
    Z: Float32[Flat],
    DLAMBDA: Float32[Flat],
    W: Float32[Flat],
    Q2: Float32[Flat],
    INDX: Int32[Flat],
    INDXC: Int32[Flat],
    INDXP: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAED3")
@external
def slaed3(
    K: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    RHO: Ref(Float32),
    DLAMBDA: Float32[Flat],
    Q2: Float32[Flat],
    INDX: Int32[Flat],
    CTOT: Int32[Flat],
    W: Float32[Flat],
    S: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAED4")
@external
def slaed4(
    N: Ref(Int32),
    I: Ref(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    DELTA: Float32[Flat],
    RHO: Ref(Float32),
    DLAM: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAED5")
@external
def slaed5(
    I: Ref(Int32),
    D: Float32[2],
    Z: Float32[2],
    DELTA: Float32[2],
    RHO: Ref(Float32),
    DLAM: Ref(Float32)
) -> None: ...

@bind("SLAED6")
@external
def slaed6(
    KNITER: Ref(Int32),
    ORGATI: Ref(Bool),
    RHO: Ref(Float32),
    D: Float32[3],
    Z: Float32[3],
    FINIT: Ref(Float32),
    TAU: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAED7")
@external
def slaed7(
    ICOMPQ: Ref(Int32),
    N: Ref(Int32),
    QSIZ: Ref(Int32),
    TLVLS: Ref(Int32),
    CURLVL: Ref(Int32),
    CURPBM: Ref(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    INDXQ: Int32[Flat],
    RHO: Ref(Float32),
    CUTPNT: Ref(Int32),
    QSTORE: Float32[Flat],
    QPTR: Int32[Flat],
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAED8")
@external
def slaed8(
    ICOMPQ: Ref(Int32),
    K: Ref(Int32),
    N: Ref(Int32),
    QSIZ: Ref(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    INDXQ: Int32[Flat],
    RHO: Ref(Float32),
    CUTPNT: Ref(Int32),
    Z: Float32[Flat],
    DLAMBDA: Float32[Flat],
    Q2: Float32[LDQ2, Flat],
    LDQ2: Ref(Int32),
    W: Float32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAED9")
@external
def slaed9(
    K: Ref(Int32),
    KSTART: Ref(Int32),
    KSTOP: Ref(Int32),
    N: Ref(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    RHO: Ref(Float32),
    DLAMBDA: Float32[Flat],
    W: Float32[Flat],
    S: Float32[LDS, Flat],
    LDS: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAEDA")
@external
def slaeda(
    N: Ref(Int32),
    TLVLS: Ref(Int32),
    CURLVL: Ref(Int32),
    CURPBM: Ref(Int32),
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    Q: Float32[Flat],
    QPTR: Int32[Flat],
    Z: Float32[Flat],
    ZTEMP: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAEIN")
@external
def slaein(
    RIGHTV: Ref(Bool),
    NOINIT: Ref(Bool),
    N: Ref(Int32),
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    WR: Ref(Float32),
    WI: Ref(Float32),
    VR: Float32[Flat],
    VI: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    EPS3: Ref(Float32),
    SMLNUM: Ref(Float32),
    BIGNUM: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAEV2")
@external
def slaev2(
    A: Ref(Float32),
    B: Ref(Float32),
    C: Ref(Float32),
    RT1: Ref(Float32),
    RT2: Ref(Float32),
    CS1: Ref(Float32),
    SN1: Ref(Float32)
) -> None: ...

@bind("SLAEXC")
@external
def slaexc(
    WANTQ: Ref(Bool),
    N: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    J1: Ref(Int32),
    N1: Ref(Int32),
    N2: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAG2")
@external
def slag2(
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    SAFMIN: Ref(Float32),
    SCALE1: Ref(Float32),
    SCALE2: Ref(Float32),
    WR1: Ref(Float32),
    WR2: Ref(Float32),
    WI: Ref(Float32)
) -> None: ...

@bind("SLAG2D")
@external
def slag2d(
    M: Ref(Int32),
    N: Ref(Int32),
    SA: Float32[LDSA, Flat],
    LDSA: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAGS2")
@external
def slags2(
    UPPER: Ref(Bool),
    A1: Ref(Float32),
    A2: Ref(Float32),
    A3: Ref(Float32),
    B1: Ref(Float32),
    B2: Ref(Float32),
    B3: Ref(Float32),
    CSU: Ref(Float32),
    SNU: Ref(Float32),
    CSV: Ref(Float32),
    SNV: Ref(Float32),
    CSQ: Ref(Float32),
    SNQ: Ref(Float32)
) -> None: ...

@bind("SLAGTF")
@external
def slagtf(
    N: Ref(Int32),
    A: Float32[Flat],
    LAMBDA: Ref(Float32),
    B: Float32[Flat],
    C: Float32[Flat],
    TOL: Ref(Float32),
    D: Float32[Flat],
    IN: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAGTM")
@external
def slagtm(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    ALPHA: Ref(Float32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    BETA: Ref(Float32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("SLAGTS")
@external
def slagts(
    JOB: Ref(Int32),
    N: Ref(Int32),
    A: Float32[Flat],
    B: Float32[Flat],
    C: Float32[Flat],
    D: Float32[Flat],
    IN: Int32[Flat],
    Y: Float32[Flat],
    TOL: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAGV2")
@external
def slagv2(
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    ALPHAR: Float32[2],
    ALPHAI: Float32[2],
    BETA: Float32[2],
    CSL: Ref(Float32),
    SNL: Ref(Float32),
    CSR: Ref(Float32),
    SNR: Ref(Float32)
) -> None: ...

@bind("SLAHQR")
@external
def slahqr(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAHR2")
@external
def slahr2(
    N: Ref(Int32),
    K: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[NB],
    T: Annotated[Float32[LDT, NB], ORDER_F],
    LDT: Ref(Int32),
    Y: Annotated[Float32[LDY, NB], ORDER_F],
    LDY: Ref(Int32)
) -> None: ...

@bind("SLAIC1")
@external
def slaic1(
    JOB: Ref(Int32),
    J: Ref(Int32),
    X: Float32[J],
    SEST: Ref(Float32),
    W: Float32[J],
    GAMMA: Ref(Float32),
    SESTPR: Ref(Float32),
    S: Ref(Float32),
    C: Ref(Float32)
) -> None: ...

@bind("SLAISNAN")
@external
@native_call([Ref(Arg(0)), Ref(Arg(1))])
def slaisnan(
    SIN1: Const(Float32),
    SIN2: Const(Float32)
) -> Bool: ...

@bind("SLALN2")
@external
def slaln2(
    LTRANS: Ref(Bool),
    NA: Ref(Int32),
    NW: Ref(Int32),
    SMIN: Ref(Float32),
    CA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D1: Ref(Float32),
    D2: Ref(Float32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WR: Ref(Float32),
    WI: Ref(Float32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    SCALE: Ref(Float32),
    XNORM: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLALS0")
@external
def slals0(
    ICOMPQ: Ref(Int32),
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    NRHS: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    BX: Float32[LDBX, Flat],
    LDBX: Ref(Int32),
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Ref(Int32),
    POLES: Float32[LDGNUM, Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[LDGNUM, Flat],
    Z: Float32[Flat],
    K: Ref(Int32),
    C: Ref(Float32),
    S: Ref(Float32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLALSA")
@external
def slalsa(
    ICOMPQ: Ref(Int32),
    SMLSIZ: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    BX: Float32[LDBX, Flat],
    LDBX: Ref(Int32),
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float32[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float32[LDU, Flat],
    DIFR: Float32[LDU, Flat],
    Z: Float32[LDU, Flat],
    POLES: Float32[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float32[LDU, Flat],
    C: Float32[Flat],
    S: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLALSD")
@external
def slalsd(
    UPLO: Ref(Const(String[1])),
    SMLSIZ: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    RCOND: Ref(Float32),
    RANK: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAMRG")
@external
def slamrg(
    N1: Ref(Int32),
    N2: Ref(Int32),
    A: Float32[Flat],
    STRD1: Ref(Int32),
    STRD2: Ref(Int32),
    INDEX: Int32[Flat]
) -> None: ...

@bind("SLAMSWLQ")
@external
def slamswlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAMTSQR")
@external
def slamtsqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLANEG")
@external
def slaneg(
    N: Ref(Int32),
    D: Float32[Flat],
    LLD: Float32[Flat],
    SIGMA: Ref(Float32),
    PIVMIN: Ref(Float32),
    R: Ref(Int32)
) -> Int32: ...

@bind("SLANGB")
@external
def slangb(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANGE")
@external
def slange(
    NORM: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANGT")
@external
def slangt(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat]
) -> Float32: ...

@bind("SLANHS")
@external
def slanhs(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANSB")
@external
def slansb(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANSF")
@external
def slansf(
    NORM: Ref(Const(String[1])),
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    WORK: Annotated[Float32[Flat], SourceDims("0:*")]
) -> Float32: ...

@bind("SLANSP")
@external
def slansp(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANST")
@external
def slanst(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat]
) -> Float32: ...

@bind("SLANSY")
@external
def slansy(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANTB")
@external
def slantb(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANTP")
@external
def slantp(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANTR")
@external
def slantr(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANV2")
@external
def slanv2(
    A: Ref(Float32),
    B: Ref(Float32),
    C: Ref(Float32),
    D: Ref(Float32),
    RT1R: Ref(Float32),
    RT1I: Ref(Float32),
    RT2R: Ref(Float32),
    RT2I: Ref(Float32),
    CS: Ref(Float32),
    SN: Ref(Float32)
) -> None: ...

@bind("SLAORHR_COL_GETRFNP")
@external
def slaorhr_col_getrfnp(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAORHR_COL_GETRFNP2")
@external
def slaorhr_col_getrfnp2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAPLL")
@external
def slapll(
    N: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    Y: Float32[Flat],
    INCY: Ref(Int32),
    SSMIN: Ref(Float32)
) -> None: ...

@bind("SLAPMR")
@external
def slapmr(
    FORWRD: Ref(Bool),
    M: Ref(Int32),
    N: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("SLAPMT")
@external
def slapmt(
    FORWRD: Ref(Bool),
    M: Ref(Int32),
    N: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("SLAPY2")
@external
def slapy2(
    X: Ref(Float32),
    Y: Ref(Float32)
) -> Float32: ...

@bind("SLAPY3")
@external
def slapy3(
    X: Ref(Float32),
    Y: Ref(Float32),
    Z: Ref(Float32)
) -> Float32: ...

@bind("SLAQGB")
@external
def slaqgb(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("SLAQGE")
@external
def slaqge(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ref(Float32),
    COLCND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("SLAQP2")
@external
def slaqp2(
    M: Ref(Int32),
    N: Ref(Int32),
    OFFSET: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Float32[Flat]
) -> None: ...

@bind("SLAQP2RK")
@external
def slaqp2rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    IOFFSET: Ref(Int32),
    KMAX: Ref(Int32),
    ABSTOL: Ref(Float32),
    RELTOL: Ref(Float32),
    KP1: Ref(Int32),
    MAXC2NRM: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    K: Ref(Int32),
    MAXC2NRMK: Ref(Float32),
    RELMAXC2NRMK: Ref(Float32),
    JPIV: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAQP3RK")
@external
def slaqp3rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    IOFFSET: Ref(Int32),
    NB: Ref(Int32),
    ABSTOL: Ref(Float32),
    RELTOL: Ref(Float32),
    KP1: Ref(Int32),
    MAXC2NRM: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    DONE: Ref(Bool),
    KB: Ref(Int32),
    MAXC2NRMK: Ref(Float32),
    RELMAXC2NRMK: Ref(Float32),
    JPIV: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Float32[Flat],
    F: Float32[LDF, Flat],
    LDF: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAQPS")
@external
def slaqps(
    M: Ref(Int32),
    N: Ref(Int32),
    OFFSET: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Float32[Flat],
    F: Float32[LDF, Flat],
    LDF: Ref(Int32)
) -> None: ...

@bind("SLAQR0")
@external
def slaqr0(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAQR1")
@external
def slaqr1(
    N: Ref(Int32),
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    SR1: Ref(Float32),
    SI1: Ref(Float32),
    SR2: Ref(Float32),
    SI2: Ref(Float32),
    V: Float32[Flat]
) -> None: ...

@bind("SLAQR2")
@external
def slaqr2(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NW: Ref(Int32),
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    NS: Ref(Int32),
    ND: Ref(Int32),
    SR: Float32[Flat],
    SI: Float32[Flat],
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    NH: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    NV: Ref(Int32),
    WV: Float32[LDWV, Flat],
    LDWV: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32)
) -> None: ...

@bind("SLAQR3")
@external
def slaqr3(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NW: Ref(Int32),
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    NS: Ref(Int32),
    ND: Ref(Int32),
    SR: Float32[Flat],
    SI: Float32[Flat],
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    NH: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    NV: Ref(Int32),
    WV: Float32[LDWV, Flat],
    LDWV: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32)
) -> None: ...

@bind("SLAQR4")
@external
def slaqr4(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAQR5")
@external
def slaqr5(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    KACC22: Ref(Int32),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NSHFTS: Ref(Int32),
    SR: Float32[Flat],
    SI: Float32[Flat],
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    NV: Ref(Int32),
    WV: Float32[LDWV, Flat],
    LDWV: Ref(Int32),
    NH: Ref(Int32),
    WH: Float32[LDWH, Flat],
    LDWH: Ref(Int32)
) -> None: ...

@bind("SLAQSB")
@external
def slaqsb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("SLAQSP")
@external
def slaqsp(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("SLAQSY")
@external
def slaqsy(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("SLAQTR")
@external
def slaqtr(
    LTRAN: Ref(Bool),
    LREAL: Ref(Bool),
    N: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    B: Float32[Flat],
    W: Ref(Float32),
    SCALE: Ref(Float32),
    X: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Arg(6), Ref(Arg(7)), Arg(8), Ref(Arg(9)), Arg(10), Arg(11), Arg(12), Arg(13), Ref(Arg(14)), Arg(15), Ref(Arg(16)), Arg(17), Ref(Arg(18)), Ref(Arg(19)), Return('INFO', 0)])
def slaqz0(
    WANTS: Ref(Const(String[1])),
    WANTQ: Ref(Const(String[1])),
    WANTZ: Ref(Const(String[1])),
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
@native_call([Arg(0), Ref(Arg(1)), Arg(2), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Ref(Arg(7)), Ref(Arg(8)), Arg(9)])
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Arg(6), Ref(Arg(7)), Arg(8), Ref(Arg(9)), Ref(Arg(10)), Ref(Arg(11)), Arg(12), Ref(Arg(13)), Ref(Arg(14)), Ref(Arg(15)), Arg(16), Ref(Arg(17))])
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Arg(7), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Arg(11), Ref(Arg(12)), Arg(13), Ref(Arg(14)), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Arg(18), Ref(Arg(19)), Arg(20), Ref(Arg(21)), Arg(22), Ref(Arg(23)), Ref(Arg(24)), Return('INFO', 2)])
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Ref(Arg(7)), Arg(8), Arg(9), Arg(10), Arg(11), Ref(Arg(12)), Arg(13), Ref(Arg(14)), Arg(15), Ref(Arg(16)), Arg(17), Ref(Arg(18)), Arg(19), Ref(Arg(20)), Arg(21), Ref(Arg(22)), Arg(23), Ref(Arg(24)), Return('INFO', 0)])
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
    N: Ref(Int32),
    B1: Ref(Int32),
    BN: Ref(Int32),
    LAMBDA: Ref(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    LD: Float32[Flat],
    LLD: Float32[Flat],
    PIVMIN: Ref(Float32),
    GAPTOL: Ref(Float32),
    Z: Float32[Flat],
    WANTNC: Ref(Bool),
    NEGCNT: Ref(Int32),
    ZTZ: Ref(Float32),
    MINGMA: Ref(Float32),
    R: Ref(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Ref(Float32),
    RESID: Ref(Float32),
    RQCORR: Ref(Float32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLAR2V")
@external
def slar2v(
    N: Ref(Int32),
    X: Float32[Flat],
    Y: Float32[Flat],
    Z: Float32[Flat],
    INCX: Ref(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("SLARF")
@external
def slarf(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Float32[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARF1F")
@external
def slarf1f(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Float32[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARF1L")
@external
def slarf1l(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Float32[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARFB")
@external
def slarfb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("SLARFB_GETT")
@external
def slarfb_gett(
    IDENT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("SLARFG")
@external
def slarfg(
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    TAU: Ref(Float32)
) -> None: ...

@bind("SLARFGP")
@external
def slarfgp(
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    TAU: Ref(Float32)
) -> None: ...

@bind("SLARFT")
@external
def slarft(
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    TAU: Float32[Flat],
    T: Float32[LDT, Flat],
    LDT: Ref(Int32)
) -> None: ...

@bind("SLARFX")
@external
def slarfx(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Float32[Flat],
    TAU: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARFY")
@external
def slarfy(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    V: Float32[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARGV")
@external
def slargv(
    N: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    Y: Float32[Flat],
    INCY: Ref(Int32),
    C: Float32[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("SLARMM")
@external
def slarmm(
    ANORM: Ref(Float32),
    BNORM: Ref(Float32),
    CNORM: Ref(Float32)
) -> Float32: ...

@bind("SLARNV")
@external
def slarnv(
    IDIST: Ref(Int32),
    ISEED: Int32[4],
    N: Ref(Int32),
    X: Float32[Flat]
) -> None: ...

@bind("SLARRA")
@external
def slarra(
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    SPLTOL: Ref(Float32),
    TNRM: Ref(Float32),
    NSPLIT: Ref(Int32),
    ISPLIT: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLARRB")
@external
def slarrb(
    N: Ref(Int32),
    D: Float32[Flat],
    LLD: Float32[Flat],
    IFIRST: Ref(Int32),
    ILAST: Ref(Int32),
    RTOL1: Ref(Float32),
    RTOL2: Ref(Float32),
    OFFSET: Ref(Int32),
    W: Float32[Flat],
    WGAP: Float32[Flat],
    WERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Ref(Float32),
    SPDIAM: Ref(Float32),
    TWIST: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLARRC")
@external
def slarrc(
    JOBT: Ref(Const(String[1])),
    N: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    PIVMIN: Ref(Float32),
    EIGCNT: Ref(Int32),
    LCNT: Ref(Int32),
    RCNT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLARRD")
@external
def slarrd(
    RANGE: Ref(Const(String[1])),
    ORDER: Ref(Const(String[1])),
    N: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    GERS: Float32[Flat],
    RELTOL: Ref(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    PIVMIN: Ref(Float32),
    NSPLIT: Ref(Int32),
    ISPLIT: Int32[Flat],
    M: Ref(Int32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WL: Ref(Float32),
    WU: Ref(Float32),
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLARRE")
@external
def slarre(
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    RTOL1: Ref(Float32),
    RTOL2: Ref(Float32),
    SPLTOL: Ref(Float32),
    NSPLIT: Ref(Int32),
    ISPLIT: Int32[Flat],
    M: Ref(Int32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WGAP: Float32[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float32[Flat],
    PIVMIN: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLARRF")
@external
def slarrf(
    N: Ref(Int32),
    D: Float32[Flat],
    L: Float32[Flat],
    LD: Float32[Flat],
    CLSTRT: Ref(Int32),
    CLEND: Ref(Int32),
    W: Float32[Flat],
    WGAP: Float32[Flat],
    WERR: Float32[Flat],
    SPDIAM: Ref(Float32),
    CLGAPL: Ref(Float32),
    CLGAPR: Ref(Float32),
    PIVMIN: Ref(Float32),
    SIGMA: Ref(Float32),
    DPLUS: Float32[Flat],
    LPLUS: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLARRJ")
@external
def slarrj(
    N: Ref(Int32),
    D: Float32[Flat],
    E2: Float32[Flat],
    IFIRST: Ref(Int32),
    ILAST: Ref(Int32),
    RTOL: Ref(Float32),
    OFFSET: Ref(Int32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Ref(Float32),
    SPDIAM: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLARRK")
@external
def slarrk(
    N: Ref(Int32),
    IW: Ref(Int32),
    GL: Ref(Float32),
    GU: Ref(Float32),
    D: Float32[Flat],
    E2: Float32[Flat],
    PIVMIN: Ref(Float32),
    RELTOL: Ref(Float32),
    W: Ref(Float32),
    WERR: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLARRR")
@external
def slarrr(
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLARRV")
@external
def slarrv(
    N: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    PIVMIN: Ref(Float32),
    ISPLIT: Int32[Flat],
    M: Ref(Int32),
    DOL: Ref(Int32),
    DOU: Ref(Int32),
    MINRGP: Ref(Float32),
    RTOL1: Ref(Float32),
    RTOL2: Ref(Float32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WGAP: Float32[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLARSCL2")
@external
def slarscl2(
    M: Ref(Int32),
    N: Ref(Int32),
    D: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Ref(Int32)
) -> None: ...

@bind("SLARTG")
@external
def slartg(
    f: Ref(Float32),
    g: Ref(Float32),
    c: Ref(Float32),
    s: Ref(Float32),
    r: Ref(Float32)
) -> None: ...

@bind("SLARTGP")
@external
def slartgp(
    F: Ref(Float32),
    G: Ref(Float32),
    CS: Ref(Float32),
    SN: Ref(Float32),
    R: Ref(Float32)
) -> None: ...

@bind("SLARTGS")
@external
def slartgs(
    X: Ref(Float32),
    Y: Ref(Float32),
    SIGMA: Ref(Float32),
    CS: Ref(Float32),
    SN: Ref(Float32)
) -> None: ...

@bind("SLARTV")
@external
def slartv(
    N: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    Y: Float32[Flat],
    INCY: Ref(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("SLARUV")
@external
def slaruv(
    ISEED: Int32[4],
    N: Ref(Int32),
    X: Float32[N]
) -> None: ...

@bind("SLARZ")
@external
def slarz(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    V: Float32[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARZB")
@external
def slarzb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("SLARZT")
@external
def slarzt(
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    TAU: Float32[Flat],
    T: Float32[LDT, Flat],
    LDT: Ref(Int32)
) -> None: ...

@bind("SLAS2")
@external
def slas2(
    F: Ref(Float32),
    G: Ref(Float32),
    H: Ref(Float32),
    SSMIN: Ref(Float32),
    SSMAX: Ref(Float32)
) -> None: ...

@bind("SLASCL")
@external
def slascl(
    TYPE: Ref(Const(String[1])),
    KL: Ref(Int32),
    KU: Ref(Int32),
    CFROM: Ref(Float32),
    CTO: Ref(Float32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASCL2")
@external
def slascl2(
    M: Ref(Int32),
    N: Ref(Int32),
    D: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Ref(Int32)
) -> None: ...

@bind("SLASD0")
@external
def slasd0(
    N: Ref(Int32),
    SQRE: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ref(Int32),
    SMLSIZ: Ref(Int32),
    IWORK: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASD1")
@external
def slasd1(
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    D: Float32[Flat],
    ALPHA: Ref(Float32),
    BETA: Ref(Float32),
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ref(Int32),
    IDXQ: Int32[Flat],
    IWORK: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASD2")
@external
def slasd2(
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    K: Ref(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    ALPHA: Ref(Float32),
    BETA: Ref(Float32),
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ref(Int32),
    DSIGMA: Float32[Flat],
    U2: Float32[LDU2, Flat],
    LDU2: Ref(Int32),
    VT2: Float32[LDVT2, Flat],
    LDVT2: Ref(Int32),
    IDXP: Int32[Flat],
    IDX: Int32[Flat],
    IDXC: Int32[Flat],
    IDXQ: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASD3")
@external
def slasd3(
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    K: Ref(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    DSIGMA: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Ref(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ref(Int32),
    VT2: Float32[LDVT2, Flat],
    LDVT2: Ref(Int32),
    IDXC: Int32[Flat],
    CTOT: Int32[Flat],
    Z: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASD4")
@external
def slasd4(
    N: Ref(Int32),
    I: Ref(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    DELTA: Float32[Flat],
    RHO: Ref(Float32),
    SIGMA: Ref(Float32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASD5")
@external
def slasd5(
    I: Ref(Int32),
    D: Float32[2],
    Z: Float32[2],
    DELTA: Float32[2],
    RHO: Ref(Float32),
    DSIGMA: Ref(Float32),
    WORK: Float32[2]
) -> None: ...

@bind("SLASD6")
@external
def slasd6(
    ICOMPQ: Ref(Int32),
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    D: Float32[Flat],
    VF: Float32[Flat],
    VL: Float32[Flat],
    ALPHA: Ref(Float32),
    BETA: Ref(Float32),
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Ref(Int32),
    POLES: Float32[LDGNUM, Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[Flat],
    Z: Float32[Flat],
    K: Ref(Int32),
    C: Ref(Float32),
    S: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASD7")
@external
def slasd7(
    ICOMPQ: Ref(Int32),
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    K: Ref(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    ZW: Float32[Flat],
    VF: Float32[Flat],
    VFW: Float32[Flat],
    VL: Float32[Flat],
    VLW: Float32[Flat],
    ALPHA: Ref(Float32),
    BETA: Ref(Float32),
    DSIGMA: Float32[Flat],
    IDX: Int32[Flat],
    IDXP: Int32[Flat],
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Ref(Int32),
    C: Ref(Float32),
    S: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASD8")
@external
def slasd8(
    ICOMPQ: Ref(Int32),
    K: Ref(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    VF: Float32[Flat],
    VL: Float32[Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[LDDIFR, Flat],
    LDDIFR: Ref(Int32),
    DSIGMA: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASDA")
@external
def slasda(
    ICOMPQ: Ref(Int32),
    SMLSIZ: Ref(Int32),
    N: Ref(Int32),
    SQRE: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float32[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float32[LDU, Flat],
    DIFR: Float32[LDU, Flat],
    Z: Float32[LDU, Flat],
    POLES: Float32[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float32[LDU, Flat],
    C: Float32[Flat],
    S: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASDQ")
@external
def slasdq(
    UPLO: Ref(Const(String[1])),
    SQRE: Ref(Int32),
    N: Ref(Int32),
    NCVT: Ref(Int32),
    NRU: Ref(Int32),
    NCC: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VT: Float32[LDVT, Flat],
    LDVT: Ref(Int32),
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASDT")
@external
def slasdt(
    N: Ref(Int32),
    LVL: Ref(Int32),
    ND: Ref(Int32),
    INODE: Int32[Flat],
    NDIML: Int32[Flat],
    NDIMR: Int32[Flat],
    MSUB: Ref(Int32)
) -> None: ...

@bind("SLASET")
@external
def slaset(
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    BETA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("SLASQ1")
@external
def slasq1(
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASQ2")
@external
def slasq2(
    N: Ref(Int32),
    Z: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASQ3")
@external
def slasq3(
    I0: Ref(Int32),
    N0: Ref(Int32),
    Z: Float32[Flat],
    PP: Ref(Int32),
    DMIN: Ref(Float32),
    SIGMA: Ref(Float32),
    DESIG: Ref(Float32),
    QMAX: Ref(Float32),
    NFAIL: Ref(Int32),
    ITER: Ref(Int32),
    NDIV: Ref(Int32),
    IEEE: Ref(Bool),
    TTYPE: Ref(Int32),
    DMIN1: Ref(Float32),
    DMIN2: Ref(Float32),
    DN: Ref(Float32),
    DN1: Ref(Float32),
    DN2: Ref(Float32),
    G: Ref(Float32),
    TAU: Ref(Float32)
) -> None: ...

@bind("SLASQ4")
@external
def slasq4(
    I0: Ref(Int32),
    N0: Ref(Int32),
    Z: Float32[Flat],
    PP: Ref(Int32),
    N0IN: Ref(Int32),
    DMIN: Ref(Float32),
    DMIN1: Ref(Float32),
    DMIN2: Ref(Float32),
    DN: Ref(Float32),
    DN1: Ref(Float32),
    DN2: Ref(Float32),
    TAU: Ref(Float32),
    TTYPE: Ref(Int32),
    G: Ref(Float32)
) -> None: ...

@bind("SLASQ5")
@external
def slasq5(
    I0: Ref(Int32),
    N0: Ref(Int32),
    Z: Float32[Flat],
    PP: Ref(Int32),
    TAU: Ref(Float32),
    SIGMA: Ref(Float32),
    DMIN: Ref(Float32),
    DMIN1: Ref(Float32),
    DMIN2: Ref(Float32),
    DN: Ref(Float32),
    DNM1: Ref(Float32),
    DNM2: Ref(Float32),
    IEEE: Ref(Bool),
    EPS: Ref(Float32)
) -> None: ...

@bind("SLASQ6")
@external
def slasq6(
    I0: Ref(Int32),
    N0: Ref(Int32),
    Z: Float32[Flat],
    PP: Ref(Int32),
    DMIN: Ref(Float32),
    DMIN1: Ref(Float32),
    DMIN2: Ref(Float32),
    DN: Ref(Float32),
    DNM1: Ref(Float32),
    DNM2: Ref(Float32)
) -> None: ...

@bind("SLASR")
@external
def slasr(
    SIDE: Ref(Const(String[1])),
    PIVOT: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    A: Float32[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("SLASRT")
@external
def slasrt(
    ID: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASSQ")
@external
def slassq(
    n: Ref(Int32),
    x: Float32[Flat],
    incx: Ref(Int32),
    scale: Ref(Float32),
    sumsq: Ref(Float32)
) -> None: ...

@bind("SLASV2")
@external
def slasv2(
    F: Ref(Float32),
    G: Ref(Float32),
    H: Ref(Float32),
    SSMIN: Ref(Float32),
    SSMAX: Ref(Float32),
    SNR: Ref(Float32),
    CSR: Ref(Float32),
    SNL: Ref(Float32),
    CSL: Ref(Float32)
) -> None: ...

@bind("SLASWLQ")
@external
def slaswlq(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASWP")
@external
def slaswp(
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    K1: Ref(Int32),
    K2: Ref(Int32),
    IPIV: Int32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("SLASY2")
@external
def slasy2(
    LTRANL: Ref(Bool),
    LTRANR: Ref(Bool),
    ISGN: Ref(Int32),
    N1: Ref(Int32),
    N2: Ref(Int32),
    TL: Float32[LDTL, Flat],
    LDTL: Ref(Int32),
    TR: Float32[LDTR, Flat],
    LDTR: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    SCALE: Ref(Float32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    XNORM: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASYF")
@external
def slasyf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Float32[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASYF_AA")
@external
def slasyf_aa(
    UPLO: Ref(Const(String[1])),
    J1: Ref(Int32),
    M: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    H: Float32[LDH, Flat],
    LDH: Ref(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLASYF_RK")
@external
def slasyf_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    W: Float32[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLASYF_ROOK")
@external
def slasyf_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Float32[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLATBS")
@external
def slatbs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    X: Float32[Flat],
    SCALE: Ref(Float32),
    CNORM: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLATDF")
@external
def slatdf(
    IJOB: Ref(Int32),
    N: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    RHS: Float32[Flat],
    RDSUM: Ref(Float32),
    RDSCAL: Ref(Float32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("SLATPS")
@external
def slatps(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    X: Float32[Flat],
    SCALE: Ref(Float32),
    CNORM: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLATRD")
@external
def slatrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    TAU: Float32[Flat],
    W: Float32[LDW, Flat],
    LDW: Ref(Int32)
) -> None: ...

@bind("SLATRS")
@external
def slatrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    X: Float32[Flat],
    SCALE: Ref(Float32),
    CNORM: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SLATRS3")
@external
def slatrs3(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    SCALE: Float32[Flat],
    CNORM: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLATRZ")
@external
def slatrz(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat]
) -> None: ...

@bind("SLATSQR")
@external
def slatsqr(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAUU2")
@external
def slauu2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SLAUUM")
@external
def slauum(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SOPGTR")
@external
def sopgtr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    TAU: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SOPMTR")
@external
def sopmtr(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    AP: Float32[Flat],
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORBDB")
@external
def sorbdb(
    TRANS: Ref(Const(String[1])),
    SIGNS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ref(Int32),
    X12: Float32[LDX12, Flat],
    LDX12: Ref(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ref(Int32),
    X22: Float32[LDX22, Flat],
    LDX22: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    TAUQ2: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORBDB1")
@external
def sorbdb1(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORBDB2")
@external
def sorbdb2(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORBDB3")
@external
def sorbdb3(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORBDB4")
@external
def sorbdb4(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    PHANTOM: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORBDB5")
@external
def sorbdb5(
    M1: Ref(Int32),
    M2: Ref(Int32),
    N: Ref(Int32),
    X1: Float32[Flat],
    INCX1: Ref(Int32),
    X2: Float32[Flat],
    INCX2: Ref(Int32),
    Q1: Float32[LDQ1, Flat],
    LDQ1: Ref(Int32),
    Q2: Float32[LDQ2, Flat],
    LDQ2: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORBDB6")
@external
def sorbdb6(
    M1: Ref(Int32),
    M2: Ref(Int32),
    N: Ref(Int32),
    X1: Float32[Flat],
    INCX1: Ref(Int32),
    X2: Float32[Flat],
    INCX2: Ref(Int32),
    Q1: Float32[LDQ1, Flat],
    LDQ1: Ref(Int32),
    Q2: Float32[LDQ2, Flat],
    LDQ2: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORCSD")
@external
def sorcsd(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    JOBV2T: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    SIGNS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ref(Int32),
    X12: Float32[LDX12, Flat],
    LDX12: Ref(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ref(Int32),
    X22: Float32[LDX22, Flat],
    LDX22: Ref(Int32),
    THETA: Float32[Flat],
    U1: Float32[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Float32[LDV1T, Flat],
    LDV1T: Ref(Int32),
    V2T: Float32[LDV2T, Flat],
    LDV2T: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORCSD2BY1")
@external
def sorcsd2by1(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float32[Flat],
    U1: Float32[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Float32[LDV1T, Flat],
    LDV1T: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORG2L")
@external
def sorg2l(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORG2R")
@external
def sorg2r(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGBR")
@external
def sorgbr(
    VECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGHR")
@external
def sorghr(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGL2")
@external
def sorgl2(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGLQ")
@external
def sorglq(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGQL")
@external
def sorgql(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGQR")
@external
def sorgqr(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGR2")
@external
def sorgr2(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGRQ")
@external
def sorgrq(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGTR")
@external
def sorgtr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGTSQR")
@external
def sorgtsqr(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORGTSQR_ROW")
@external
def sorgtsqr_row(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORHR_COL")
@external
def sorhr_col(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    D: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORM22")
@external
def sorm22(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    N2: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORM2L")
@external
def sorm2l(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORM2R")
@external
def sorm2r(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORMBR")
@external
def sormbr(
    VECT: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORMHR")
@external
def sormhr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORML2")
@external
def sorml2(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORMLQ")
@external
def sormlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORMQL")
@external
def sormql(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORMQR")
@external
def sormqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORMR2")
@external
def sormr2(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORMR3")
@external
def sormr3(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SORMRQ")
@external
def sormrq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORMRZ")
@external
def sormrz(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SORMTR")
@external
def sormtr(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPBCON")
@external
def spbcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPBEQU")
@external
def spbequ(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPBRFS")
@external
def spbrfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPBSTF")
@external
def spbstf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPBSV")
@external
def spbsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPBSVX")
@external
def spbsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPBTF2")
@external
def spbtf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPBTRF")
@external
def spbtrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPBTRS")
@external
def spbtrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPFTRF")
@external
def spftrf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPFTRI")
@external
def spftri(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPFTRS")
@external
def spftrs(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOCON")
@external
def spocon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOEQU")
@external
def spoequ(
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOEQUB")
@external
def spoequb(
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPORFS")
@external
def sporfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPORFSX")
@external
def sporfsx(
    UPLO: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOSV")
@external
def sposv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOSVX")
@external
def sposvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOSVXX")
@external
def sposvxx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    RPVGRW: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOTF2")
@external
def spotf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOTRF")
@external
def spotrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOTRF2")
@external
def spotrf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOTRI")
@external
def spotri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPOTRS")
@external
def spotrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPPCON")
@external
def sppcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPPEQU")
@external
def sppequ(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPPRFS")
@external
def spprfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPPSV")
@external
def sppsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPPSVX")
@external
def sppsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPPTRF")
@external
def spptrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPPTRI")
@external
def spptri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPPTRS")
@external
def spptrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPSTF2")
@external
def spstf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    PIV: Int32[N],
    RANK: Ref(Int32),
    TOL: Ref(Float32),
    WORK: Float32[2 * N],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPSTRF")
@external
def spstrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    PIV: Int32[N],
    RANK: Ref(Int32),
    TOL: Ref(Float32),
    WORK: Float32[2 * N],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPTCON")
@external
def sptcon(
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPTEQR")
@external
def spteqr(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPTRFS")
@external
def sptrfs(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    DF: Float32[Flat],
    EF: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPTSV")
@external
def sptsv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPTSVX")
@external
def sptsvx(
    FACT: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    DF: Float32[Flat],
    EF: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPTTRF")
@external
def spttrf(
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SPTTRS")
@external
def spttrs(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SPTTS2")
@external
def sptts2(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("SRSCL")
@external
def srscl(
    N: Ref(Int32),
    SA: Ref(Float32),
    SX: Float32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("SSB2ST_KERNELS")
@external
def ssb2st_kernels(
    UPLO: Ref(Const(String[1])),
    WANTZ: Ref(Bool),
    TTYPE: Ref(Int32),
    ST: Ref(Int32),
    ED: Ref(Int32),
    SWEEP: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    IB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    V: Float32[Flat],
    TAU: Float32[Flat],
    LDVT: Ref(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SSBEV")
@external
def ssbev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSBEV_2STAGE")
@external
def ssbev_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSBEVD")
@external
def ssbevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSBEVD_2STAGE")
@external
def ssbevd_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSBEVX")
@external
def ssbevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSBEVX_2STAGE")
@external
def ssbevx_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSBGST")
@external
def ssbgst(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSBGV")
@external
def ssbgv(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSBGVD")
@external
def ssbgvd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSBGVX")
@external
def ssbgvx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSBTRD")
@external
def ssbtrd(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSFRK")
@external
def ssfrk(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    BETA: Ref(Float32),
    C: Float32[Flat]
) -> None: ...

@bind("SSPCON")
@external
def sspcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPEV")
@external
def sspev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPEVD")
@external
def sspevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPEVX")
@external
def sspevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPGST")
@external
def sspgst(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPGV")
@external
def sspgv(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPGVD")
@external
def sspgvd(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPGVX")
@external
def sspgvx(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPRFS")
@external
def ssprfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPSV")
@external
def sspsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPSVX")
@external
def sspsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPTRD")
@external
def ssptrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPTRF")
@external
def ssptrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPTRI")
@external
def ssptri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSPTRS")
@external
def ssptrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTEBZ")
@external
def sstebz(
    RANGE: Ref(Const(String[1])),
    ORDER: Ref(Const(String[1])),
    N: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    M: Ref(Int32),
    NSPLIT: Ref(Int32),
    W: Float32[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTEDC")
@external
def sstedc(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTEGR")
@external
def sstegr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTEIN")
@external
def sstein(
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    M: Ref(Int32),
    W: Float32[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTEMR")
@external
def sstemr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    NZC: Ref(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Ref(Bool),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTEQR")
@external
def ssteqr(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTERF")
@external
def ssterf(
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTEV")
@external
def sstev(
    JOBZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTEVD")
@external
def sstevd(
    JOBZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTEVR")
@external
def sstevr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSTEVX")
@external
def sstevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYCON")
@external
def ssycon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYCON_3")
@external
def ssycon_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYCON_ROOK")
@external
def ssycon_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYCONV")
@external
def ssyconv(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    E: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYCONVF")
@external
def ssyconvf(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYCONVF_ROOK")
@external
def ssyconvf_rook(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYEQUB")
@external
def ssyequb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    S: Float32[Flat],
    SCOND: Ref(Float32),
    AMAX: Ref(Float32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYEV")
@external
def ssyev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYEV_2STAGE")
@external
def ssyev_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYEVD")
@external
def ssyevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYEVD_2STAGE")
@external
def ssyevd_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYEVR")
@external
def ssyevr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYEVR_2STAGE")
@external
def ssyevr_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYEVX")
@external
def ssyevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYEVX_2STAGE")
@external
def ssyevx_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYGS2")
@external
def ssygs2(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYGST")
@external
def ssygst(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYGV")
@external
def ssygv(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYGV_2STAGE")
@external
def ssygv_2stage(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYGVD")
@external
def ssygvd(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYGVX")
@external
def ssygvx(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    VL: Ref(Float32),
    VU: Ref(Float32),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float32),
    M: Ref(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYRFS")
@external
def ssyrfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYRFSX")
@external
def ssyrfsx(
    UPLO: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYSV")
@external
def ssysv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYSV_AA")
@external
def ssysv_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYSV_AA_2STAGE")
@external
def ssysv_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TB: Float32[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYSV_RK")
@external
def ssysv_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYSV_ROOK")
@external
def ssysv_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYSVX")
@external
def ssysvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYSVXX")
@external
def ssysvxx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float32),
    RPVGRW: Ref(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYSWAPR")
@external
def ssyswapr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    I1: Ref(Int32),
    I2: Ref(Int32)
) -> None: ...

@bind("SSYTD2")
@external
def ssytd2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTF2")
@external
def ssytf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTF2_RK")
@external
def ssytf2_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTF2_ROOK")
@external
def ssytf2_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRD")
@external
def ssytrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRD_2STAGE")
@external
def ssytrd_2stage(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    HOUS2: Float32[Flat],
    LHOUS2: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRD_SB2ST")
@external
def ssytrd_sb2st(
    STAGE1: Ref(Const(String[1])),
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    HOUS: Float32[Flat],
    LHOUS: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRD_SY2SB")
@external
def ssytrd_sy2sb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRF")
@external
def ssytrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRF_AA")
@external
def ssytrf_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRF_AA_2STAGE")
@external
def ssytrf_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TB: Float32[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRF_RK")
@external
def ssytrf_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRF_ROOK")
@external
def ssytrf_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRI")
@external
def ssytri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRI2")
@external
def ssytri2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRI2X")
@external
def ssytri2x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRI_3")
@external
def ssytri_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRI_3X")
@external
def ssytri_3x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRI_ROOK")
@external
def ssytri_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRS")
@external
def ssytrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRS2")
@external
def ssytrs2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRS_3")
@external
def ssytrs_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRS_AA")
@external
def ssytrs_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRS_AA_2STAGE")
@external
def ssytrs_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TB: Float32[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("SSYTRS_ROOK")
@external
def ssytrs_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STBCON")
@external
def stbcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STBRFS")
@external
def stbrfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STBTRS")
@external
def stbtrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STFSM")
@external
def stfsm(
    TRANSR: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    B: Annotated[Float32[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Ref(Int32)
) -> None: ...

@bind("STFTRI")
@external
def stftri(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("STFTTP")
@external
def stfttp(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    AP: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("STFTTR")
@external
def stfttr(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    A: Annotated[Float32[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STGEVC")
@external
def stgevc(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    S: Float32[LDS, Flat],
    LDS: Ref(Int32),
    P: Float32[LDP, Flat],
    LDP: Ref(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STGEX2")
@external
def stgex2(
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    J1: Ref(Int32),
    N1: Ref(Int32),
    N2: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STGEXC")
@external
def stgexc(
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    IFST: Ref(Int32),
    ILST: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STGSEN")
@external
def stgsen(
    IJOB: Ref(Int32),
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ref(Int32),
    M: Ref(Int32),
    PL: Ref(Float32),
    PR: Ref(Float32),
    DIF: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STGSJA")
@external
def stgsja(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    TOLA: Ref(Float32),
    TOLB: Ref(Float32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Float32[Flat],
    NCYCLE: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STGSNA")
@external
def stgsna(
    JOB: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    S: Float32[Flat],
    DIF: Float32[Flat],
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STGSY2")
@external
def stgsy2(
    TRANS: Ref(Const(String[1])),
    IJOB: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    D: Float32[LDD, Flat],
    LDD: Ref(Int32),
    E: Float32[LDE, Flat],
    LDE: Ref(Int32),
    F: Float32[LDF, Flat],
    LDF: Ref(Int32),
    SCALE: Ref(Float32),
    RDSUM: Ref(Float32),
    RDSCAL: Ref(Float32),
    IWORK: Int32[Flat],
    PQ: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STGSYL")
@external
def stgsyl(
    TRANS: Ref(Const(String[1])),
    IJOB: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    D: Float32[LDD, Flat],
    LDD: Ref(Int32),
    E: Float32[LDE, Flat],
    LDE: Ref(Int32),
    F: Float32[LDF, Flat],
    LDF: Ref(Int32),
    SCALE: Ref(Float32),
    DIF: Ref(Float32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STPCON")
@external
def stpcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STPLQT")
@external
def stplqt(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    MB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STPLQT2")
@external
def stplqt2(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STPMLQT")
@external
def stpmlqt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    MB: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STPMQRT")
@external
def stpmqrt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    NB: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STPQRT")
@external
def stpqrt(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    NB: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STPQRT2")
@external
def stpqrt2(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STPRFB")
@external
def stprfb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    V: Float32[LDV, Flat],
    LDV: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("STPRFS")
@external
def stprfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STPTRI")
@external
def stptri(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STPTRS")
@external
def stptrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STPTTF")
@external
def stpttf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Annotated[Float32[Flat], SourceDims("0:*")],
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("STPTTR")
@external
def stpttr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STRCON")
@external
def strcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    RCOND: Ref(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STREVC")
@external
def strevc(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STREVC3")
@external
def strevc3(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STREXC")
@external
def strexc(
    COMPQ: Ref(Const(String[1])),
    N: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    IFST: Ref(Int32),
    ILST: Ref(Int32),
    WORK: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STRRFS")
@external
def strrfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    X: Float32[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STRSEN")
@external
def strsen(
    JOB: Ref(Const(String[1])),
    COMPQ: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ref(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    M: Ref(Int32),
    S: Ref(Float32),
    SEP: Ref(Float32),
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STRSNA")
@external
def strsna(
    JOB: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Float32[LDT, Flat],
    LDT: Ref(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ref(Int32),
    S: Float32[Flat],
    SEP: Float32[Flat],
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STRSYL")
@external
def strsyl(
    TRANA: Ref(Const(String[1])),
    TRANB: Ref(Const(String[1])),
    ISGN: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    SCALE: Ref(Float32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STRSYL3")
@external
def strsyl3(
    TRANA: Ref(Const(String[1])),
    TRANB: Ref(Const(String[1])),
    ISGN: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32),
    SCALE: Ref(Float32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    SWORK: Float32[LDSWORK, Flat],
    LDSWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STRTI2")
@external
def strti2(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STRTRI")
@external
def strtri(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STRTRS")
@external
def strtrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("STRTTF")
@external
def strttf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Float32[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ref(Int32),
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("STRTTP")
@external
def strttp(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    AP: Float32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("STZRZF")
@external
def stzrzf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
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

@bind("ZBBCSD")
@external
def zbbcsd(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    JOBV2T: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    U1: Complex128[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Complex128[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Complex128[LDV1T, Flat],
    LDV1T: Ref(Int32),
    V2T: Complex128[LDV2T, Flat],
    LDV2T: Ref(Int32),
    B11D: Float64[Flat],
    B11E: Float64[Flat],
    B12D: Float64[Flat],
    B12E: Float64[Flat],
    B21D: Float64[Flat],
    B21E: Float64[Flat],
    B22D: Float64[Flat],
    B22E: Float64[Flat],
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZBDSQR")
@external
def zbdsqr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NCVT: Ref(Int32),
    NRU: Ref(Int32),
    NCC: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VT: Complex128[LDVT, Flat],
    LDVT: Ref(Int32),
    U: Complex128[LDU, Flat],
    LDU: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZCGESV")
@external
def zcgesv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    WORK: Complex128[N, Flat],
    SWORK: Complex64[Flat],
    RWORK: Float64[Flat],
    ITER: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZCPOSV")
@external
def zcposv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    WORK: Complex128[N, Flat],
    SWORK: Complex64[Flat],
    RWORK: Float64[Flat],
    ITER: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZDRSCL")
@external
def zdrscl(
    N: Ref(Int32),
    SA: Ref(Float64),
    SX: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZGBBRD")
@external
def zgbbrd(
    VECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NCC: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    PT: Complex128[LDPT, Flat],
    LDPT: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBCON")
@external
def zgbcon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBEQU")
@external
def zgbequ(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBEQUB")
@external
def zgbequb(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBRFS")
@external
def zgbrfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBRFSX")
@external
def zgbrfsx(
    TRANS: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBSV")
@external
def zgbsv(
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBSVX")
@external
def zgbsvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBSVXX")
@external
def zgbsvxx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    RPVGRW: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBTF2")
@external
def zgbtf2(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBTRF")
@external
def zgbtrf(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGBTRS")
@external
def zgbtrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEBAK")
@external
def zgebak(
    JOB: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float64[Flat],
    M: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEBAL")
@external
def zgebal(
    JOB: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEBD2")
@external
def zgebd2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Complex128[Flat],
    TAUP: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEBRD")
@external
def zgebrd(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Complex128[Flat],
    TAUP: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGECON")
@external
def zgecon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Arg(7), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Ref(Arg(11)), Ref(Arg(12)), Return('K', 0), Arg(13), Arg(14), Ref(Arg(15)), Arg(16), Arg(17), Ref(Arg(18)), Arg(19), Ref(Arg(20)), Arg(21), Ref(Arg(22)), Arg(23), Ref(Arg(24)), Arg(25), Ref(Arg(26)), Arg(27), Ref(Arg(28)), Return('INFO', 10)])
def zgedmd(
    JOBS: Ref(Const(String[1])),
    JOBZ: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBF: Ref(Const(String[1])),
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
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Ref(Arg(6)), Ref(Arg(7)), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Arg(11), Ref(Arg(12)), Arg(13), Ref(Arg(14)), Ref(Arg(15)), Ref(Arg(16)), Return('K', 2), Arg(17), Arg(18), Ref(Arg(19)), Arg(20), Arg(21), Ref(Arg(22)), Arg(23), Ref(Arg(24)), Arg(25), Ref(Arg(26)), Arg(27), Ref(Arg(28)), Arg(29), Ref(Arg(30)), Arg(31), Ref(Arg(32)), Return('INFO', 12)])
def zgedmdq(
    JOBS: Ref(Const(String[1])),
    JOBZ: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    JOBT: Ref(Const(String[1])),
    JOBF: Ref(Const(String[1])),
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
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEEQUB")
@external
def zgeequb(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEES")
@external
def zgees(
    JOBVS: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELECT: Ref(Bool),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    SDIM: Ref(Int32),
    W: Complex128[Flat],
    VS: Complex128[LDVS, Flat],
    LDVS: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEESX")
@external
def zgeesx(
    JOBVS: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELECT: Ref(Bool),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    SDIM: Ref(Int32),
    W: Complex128[Flat],
    VS: Complex128[LDVS, Flat],
    LDVS: Ref(Int32),
    RCONDE: Ref(Float64),
    RCONDV: Ref(Float64),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEEV")
@external
def zgeev(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    W: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEEVX")
@external
def zgeevx(
    BALANC: Ref(Const(String[1])),
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    W: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    SCALE: Float64[Flat],
    ABNRM: Ref(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEHD2")
@external
def zgehd2(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEHRD")
@external
def zgehrd(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEJSV")
@external
def zgejsv(
    JOBA: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBT: Ref(Const(String[1])),
    JOBP: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    SVA: Float64[N],
    U: Complex128[LDU, Flat],
    LDU: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    CWORK: Complex128[LWORK],
    LWORK: Ref(Int32),
    RWORK: Float64[LRWORK],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGELQ")
@external
def zgelq(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[Flat],
    TSIZE: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGELQ2")
@external
def zgelq2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGELQF")
@external
def zgelqf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGELQT")
@external
def zgelqt(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGELQT3")
@external
def zgelqt3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGELS")
@external
def zgels(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGELSD")
@external
def zgelsd(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    S: Float64[Flat],
    RCOND: Ref(Float64),
    RANK: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGELSS")
@external
def zgelss(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    S: Float64[Flat],
    RCOND: Ref(Float64),
    RANK: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGELST")
@external
def zgelst(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGELSY")
@external
def zgelsy(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    JPVT: Int32[Flat],
    RCOND: Ref(Float64),
    RANK: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEMLQ")
@external
def zgemlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[Flat],
    TSIZE: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEMLQT")
@external
def zgemlqt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEMQR")
@external
def zgemqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[Flat],
    TSIZE: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEMQRT")
@external
def zgemqrt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    NB: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQL2")
@external
def zgeql2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQLF")
@external
def zgeqlf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQP3")
@external
def zgeqp3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQP3RK")
@external
def zgeqp3rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    KMAX: Ref(Int32),
    ABSTOL: Ref(Float64),
    RELTOL: Ref(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    K: Ref(Int32),
    MAXC2NRMK: Ref(Float64),
    RELMAXC2NRMK: Ref(Float64),
    JPIV: Int32[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQR")
@external
def zgeqr(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[Flat],
    TSIZE: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQR2")
@external
def zgeqr2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQR2P")
@external
def zgeqr2p(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQRF")
@external
def zgeqrf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQRFP")
@external
def zgeqrfp(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQRT")
@external
def zgeqrt(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQRT2")
@external
def zgeqrt2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGEQRT3")
@external
def zgeqrt3(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGERFS")
@external
def zgerfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGERFSX")
@external
def zgerfsx(
    TRANS: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGERQ2")
@external
def zgerq2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGERQF")
@external
def zgerqf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGESC2")
@external
def zgesc2(
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    RHS: Complex128[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Ref(Float64)
) -> None: ...

@bind("ZGESDD")
@external
def zgesdd(
    JOBZ: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ref(Int32),
    VT: Complex128[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGESV")
@external
def zgesv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGESVD")
@external
def zgesvd(
    JOBU: Ref(Const(String[1])),
    JOBVT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ref(Int32),
    VT: Complex128[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGESVDQ")
@external
def zgesvdq(
    JOBA: Ref(Const(String[1])),
    JOBP: Ref(Const(String[1])),
    JOBR: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    NUMRANK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    CWORK: Complex128[Flat],
    LCWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGESVDX")
@external
def zgesvdx(
    JOBU: Ref(Const(String[1])),
    JOBVT: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    NS: Ref(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ref(Int32),
    VT: Complex128[LDVT, Flat],
    LDVT: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGESVJ")
@external
def zgesvj(
    JOBA: Ref(Const(String[1])),
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    SVA: Float64[N],
    MV: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    CWORK: Complex128[LWORK],
    LWORK: Ref(Int32),
    RWORK: Float64[LRWORK],
    LRWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGESVX")
@external
def zgesvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGESVXX")
@external
def zgesvxx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    RPVGRW: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGETC2")
@external
def zgetc2(
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGETF2")
@external
def zgetf2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGETRF")
@external
def zgetrf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGETRF2")
@external
def zgetrf2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGETRI")
@external
def zgetri(
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGETRS")
@external
def zgetrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGETSLS")
@external
def zgetsls(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGETSQRHRT")
@external
def zgetsqrhrt(
    M: Ref(Int32),
    N: Ref(Int32),
    MB1: Ref(Int32),
    NB1: Ref(Int32),
    NB2: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGBAK")
@external
def zggbak(
    JOB: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    M: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGBAL")
@external
def zggbal(
    JOB: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGES")
@external
def zgges(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VSL: Complex128[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Complex128[LDVSR, Flat],
    LDVSR: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGES3")
@external
def zgges3(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VSL: Complex128[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Complex128[LDVSR, Flat],
    LDVSR: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGESX")
@external
def zggesx(
    JOBVSL: Ref(Const(String[1])),
    JOBVSR: Ref(Const(String[1])),
    SORT: Ref(Const(String[1])),
    SELCTG: Ref(Bool),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    SDIM: Ref(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VSL: Complex128[LDVSL, Flat],
    LDVSL: Ref(Int32),
    VSR: Complex128[LDVSR, Flat],
    LDVSR: Ref(Int32),
    RCONDE: Float64[2],
    RCONDV: Float64[2],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGEV")
@external
def zggev(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGEV3")
@external
def zggev3(
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGEVX")
@external
def zggevx(
    BALANC: Ref(Const(String[1])),
    JOBVL: Ref(Const(String[1])),
    JOBVR: Ref(Const(String[1])),
    SENSE: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    ABNRM: Ref(Float64),
    BBNRM: Ref(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGGLM")
@external
def zggglm(
    N: Ref(Int32),
    M: Ref(Int32),
    P: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    D: Complex128[Flat],
    X: Complex128[Flat],
    Y: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGHD3")
@external
def zgghd3(
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGHRD")
@external
def zgghrd(
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGLSE")
@external
def zgglse(
    M: Ref(Int32),
    N: Ref(Int32),
    P: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex128[Flat],
    D: Complex128[Flat],
    X: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGQRF")
@external
def zggqrf(
    N: Ref(Int32),
    M: Ref(Int32),
    P: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAUA: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    TAUB: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGRQF")
@external
def zggrqf(
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAUA: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    TAUB: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGSVD3")
@external
def zggsvd3(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    P: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGGSVP3")
@external
def zggsvp3(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    TOLA: Ref(Float64),
    TOLB: Ref(Float64),
    K: Ref(Int32),
    L: Ref(Int32),
    U: Complex128[LDU, Flat],
    LDU: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    IWORK: Int32[Flat],
    RWORK: Float64[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGSVJ0")
@external
def zgsvj0(
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    D: Complex128[N],
    SVA: Float64[N],
    MV: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    EPS: Ref(Float64),
    SFMIN: Ref(Float64),
    TOL: Ref(Float64),
    NSWEEP: Ref(Int32),
    WORK: Complex128[LWORK],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGSVJ1")
@external
def zgsvj1(
    JOBV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    D: Complex128[N],
    SVA: Float64[N],
    MV: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    EPS: Ref(Float64),
    SFMIN: Ref(Float64),
    TOL: Ref(Float64),
    NSWEEP: Ref(Int32),
    WORK: Complex128[LWORK],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGTCON")
@external
def zgtcon(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGTRFS")
@external
def zgtrfs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DLF: Complex128[Flat],
    DF: Complex128[Flat],
    DUF: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGTSV")
@external
def zgtsv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGTSVX")
@external
def zgtsvx(
    FACT: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DLF: Complex128[Flat],
    DF: Complex128[Flat],
    DUF: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGTTRF")
@external
def zgttrf(
    N: Ref(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGTTRS")
@external
def zgttrs(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZGTTS2")
@external
def zgtts2(
    ITRANS: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("ZHB2ST_KERNELS")
@external
def zhb2st_kernels(
    UPLO: Ref(Const(String[1])),
    WANTZ: Ref(Bool),
    TTYPE: Ref(Int32),
    ST: Ref(Int32),
    ED: Ref(Int32),
    SWEEP: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    IB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    V: Complex128[Flat],
    TAU: Complex128[Flat],
    LDVT: Ref(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZHBEV")
@external
def zhbev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHBEV_2STAGE")
@external
def zhbev_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHBEVD")
@external
def zhbevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHBEVD_2STAGE")
@external
def zhbevd_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHBEVX")
@external
def zhbevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHBEVX_2STAGE")
@external
def zhbevx_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHBGST")
@external
def zhbgst(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHBGV")
@external
def zhbgv(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHBGVD")
@external
def zhbgvd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHBGVX")
@external
def zhbgvx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KA: Ref(Int32),
    KB: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHBTRD")
@external
def zhbtrd(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHECON")
@external
def zhecon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHECON_3")
@external
def zhecon_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHECON_ROOK")
@external
def zhecon_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEEQUB")
@external
def zheequb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEEV")
@external
def zheev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEEV_2STAGE")
@external
def zheev_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEEVD")
@external
def zheevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEEVD_2STAGE")
@external
def zheevd_2stage(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEEVR")
@external
def zheevr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEEVR_2STAGE")
@external
def zheevr_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEEVX")
@external
def zheevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEEVX_2STAGE")
@external
def zheevx_2stage(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEGS2")
@external
def zhegs2(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEGST")
@external
def zhegst(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEGV")
@external
def zhegv(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEGV_2STAGE")
@external
def zhegv_2stage(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEGVD")
@external
def zhegvd(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHEGVX")
@external
def zhegvx(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHERFS")
@external
def zherfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHERFSX")
@external
def zherfsx(
    UPLO: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHESV")
@external
def zhesv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHESV_AA")
@external
def zhesv_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHESV_AA_2STAGE")
@external
def zhesv_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex128[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHESV_RK")
@external
def zhesv_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHESV_ROOK")
@external
def zhesv_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHESVX")
@external
def zhesvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHESVXX")
@external
def zhesvxx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    RPVGRW: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHESWAPR")
@external
def zheswapr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex128[LDA, N], ORDER_F],
    LDA: Ref(Int32),
    I1: Ref(Int32),
    I2: Ref(Int32)
) -> None: ...

@bind("ZHETD2")
@external
def zhetd2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETF2")
@external
def zhetf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETF2_RK")
@external
def zhetf2_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETF2_ROOK")
@external
def zhetf2_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRD")
@external
def zhetrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRD_2STAGE")
@external
def zhetrd_2stage(
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    HOUS2: Complex128[Flat],
    LHOUS2: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRD_HB2ST")
@external
def zhetrd_hb2st(
    STAGE1: Ref(Const(String[1])),
    VECT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    HOUS: Complex128[Flat],
    LHOUS: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRD_HE2HB")
@external
def zhetrd_he2hb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRF")
@external
def zhetrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRF_AA")
@external
def zhetrf_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRF_AA_2STAGE")
@external
def zhetrf_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex128[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRF_RK")
@external
def zhetrf_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRF_ROOK")
@external
def zhetrf_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRI")
@external
def zhetri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRI2")
@external
def zhetri2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRI2X")
@external
def zhetri2x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRI_3")
@external
def zhetri_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRI_3X")
@external
def zhetri_3x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRI_ROOK")
@external
def zhetri_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRS")
@external
def zhetrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRS2")
@external
def zhetrs2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRS_3")
@external
def zhetrs_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRS_AA")
@external
def zhetrs_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRS_AA_2STAGE")
@external
def zhetrs_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex128[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHETRS_ROOK")
@external
def zhetrs_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHFRK")
@external
def zhfrk(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    BETA: Ref(Float64),
    C: Complex128[Flat]
) -> None: ...

@bind("ZHGEQZ")
@external
def zhgeqz(
    JOB: Ref(Const(String[1])),
    COMPQ: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPCON")
@external
def zhpcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPEV")
@external
def zhpev(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPEVD")
@external
def zhpevd(
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPEVX")
@external
def zhpevx(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPGST")
@external
def zhpgst(
    ITYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPGV")
@external
def zhpgv(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPGVD")
@external
def zhpgvd(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPGVX")
@external
def zhpgvx(
    ITYPE: Ref(Int32),
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPRFS")
@external
def zhprfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPSV")
@external
def zhpsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPSVX")
@external
def zhpsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPTRD")
@external
def zhptrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPTRF")
@external
def zhptrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPTRI")
@external
def zhptri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHPTRS")
@external
def zhptrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHSEIN")
@external
def zhsein(
    SIDE: Ref(Const(String[1])),
    EIGSRC: Ref(Const(String[1])),
    INITV: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    W: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZHSEQR")
@external
def zhseqr(
    JOB: Ref(Const(String[1])),
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    W: Complex128[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLA_GBAMV")
@external
def zla_gbamv(
    TRANS: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    ALPHA: Ref(Float64),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float64),
    Y: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZLA_GBRCOND_C")
@external
def zla_gbrcond_c(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Ref(Bool),
    INFO: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GBRCOND_X")
@external
def zla_gbrcond_x(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GBRFSX_EXTENDED")
@external
def zla_gbrfsx_extended(
    PREC_TYPE: Ref(Int32),
    TRANS_TYPE: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Ref(Float64),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float64),
    DZ_UB: Ref(Float64),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLA_GBRPVGRW")
@external
def zla_gbrpvgrw(
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    NCOLS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ref(Int32)
) -> Float64: ...

@bind("ZLA_GEAMV")
@external
def zla_geamv(
    TRANS: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float64),
    Y: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZLA_GERCOND_C")
@external
def zla_gercond_c(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Ref(Bool),
    INFO: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GERCOND_X")
@external
def zla_gercond_x(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GERFSX_EXTENDED")
@external
def zla_gerfsx_extended(
    PREC_TYPE: Ref(Int32),
    TRANS_TYPE: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ref(Int32),
    ERRS_N: Float64[NRHS, Flat],
    ERRS_C: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Ref(Float64),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float64),
    DZ_UB: Ref(Float64),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLA_GERPVGRW")
@external
def zla_gerpvgrw(
    N: Ref(Int32),
    NCOLS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32)
) -> Float64: ...

@bind("ZLA_HEAMV")
@external
def zla_heamv(
    UPLO: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float64),
    Y: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZLA_HERCOND_C")
@external
def zla_hercond_c(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Ref(Bool),
    INFO: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_HERCOND_X")
@external
def zla_hercond_x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_HERFSX_EXTENDED")
@external
def zla_herfsx_extended(
    PREC_TYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Ref(Float64),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float64),
    DZ_UB: Ref(Float64),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLA_HERPVGRW")
@external
def zla_herpvgrw(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    INFO: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_LIN_BERR")
@external
def zla_lin_berr(
    N: Ref(Int32),
    NZ: Ref(Int32),
    NRHS: Ref(Int32),
    RES: Annotated[Complex128[N, NRHS], ORDER_F],
    AYB: Annotated[Float64[N, NRHS], ORDER_F],
    BERR: Float64[NRHS]
) -> None: ...

@bind("ZLA_PORCOND_C")
@external
def zla_porcond_c(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    C: Float64[Flat],
    CAPPLY: Ref(Bool),
    INFO: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_PORCOND_X")
@external
def zla_porcond_x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    X: Complex128[Flat],
    INFO: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_PORFSX_EXTENDED")
@external
def zla_porfsx_extended(
    PREC_TYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    COLEQU: Ref(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Ref(Float64),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float64),
    DZ_UB: Ref(Float64),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLA_PORPVGRW")
@external
def zla_porpvgrw(
    UPLO: Ref(Const(String[1])),
    NCOLS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_SYAMV")
@external
def zla_syamv(
    UPLO: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float64),
    Y: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZLA_SYRCOND_C")
@external
def zla_syrcond_c(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Ref(Bool),
    INFO: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_SYRCOND_X")
@external
def zla_syrcond_x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_SYRFSX_EXTENDED")
@external
def zla_syrfsx_extended(
    PREC_TYPE: Ref(Int32),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ref(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ref(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Ref(Float64),
    ITHRESH: Ref(Int32),
    RTHRESH: Ref(Float64),
    DZ_UB: Ref(Float64),
    IGNORE_CWISE: Ref(Bool),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLA_SYRPVGRW")
@external
def zla_syrpvgrw(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    INFO: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_WWADDW")
@external
def zla_wwaddw(
    N: Ref(Int32),
    X: Complex128[Flat],
    Y: Complex128[Flat],
    W: Complex128[Flat]
) -> None: ...

@bind("ZLABRD")
@external
def zlabrd(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Complex128[Flat],
    TAUP: Complex128[Flat],
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ref(Int32)
) -> None: ...

@bind("ZLACGV")
@external
def zlacgv(
    N: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZLACN2")
@external
def zlacn2(
    N: Ref(Int32),
    V: Complex128[Flat],
    X: Complex128[Flat],
    EST: Ref(Float64),
    KASE: Ref(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("ZLACON")
@external
def zlacon(
    N: Ref(Int32),
    V: Complex128[N],
    X: Complex128[N],
    EST: Ref(Float64),
    KASE: Ref(Int32)
) -> None: ...

@bind("ZLACP2")
@external
def zlacp2(
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("ZLACPY")
@external
def zlacpy(
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("ZLACRM")
@external
def zlacrm(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    RWORK: Float64[Flat]
) -> None: ...

@bind("ZLACRT")
@external
def zlacrt(
    N: Ref(Int32),
    CX: Complex128[Flat],
    INCX: Ref(Int32),
    CY: Complex128[Flat],
    INCY: Ref(Int32),
    C: Ref(Complex128),
    S: Ref(Complex128)
) -> None: ...

@bind("ZLADIV")
@external
def zladiv(
    X: Ref(Complex128),
    Y: Ref(Complex128)
) -> Complex128: ...

@bind("ZLAED0")
@external
def zlaed0(
    QSIZ: Ref(Int32),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    QSTORE: Complex128[LDQS, Flat],
    LDQS: Ref(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAED7")
@external
def zlaed7(
    N: Ref(Int32),
    CUTPNT: Ref(Int32),
    QSIZ: Ref(Int32),
    TLVLS: Ref(Int32),
    CURLVL: Ref(Int32),
    CURPBM: Ref(Int32),
    D: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    RHO: Ref(Float64),
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
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAED8")
@external
def zlaed8(
    K: Ref(Int32),
    N: Ref(Int32),
    QSIZ: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    D: Float64[Flat],
    RHO: Ref(Float64),
    CUTPNT: Ref(Int32),
    Z: Float64[Flat],
    DLAMBDA: Float64[Flat],
    Q2: Complex128[LDQ2, Flat],
    LDQ2: Ref(Int32),
    W: Float64[Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAEIN")
@external
def zlaein(
    RIGHTV: Ref(Bool),
    NOINIT: Ref(Bool),
    N: Ref(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    W: Ref(Complex128),
    V: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    RWORK: Float64[Flat],
    EPS3: Ref(Float64),
    SMLNUM: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAESY")
@external
def zlaesy(
    A: Ref(Complex128),
    B: Ref(Complex128),
    C: Ref(Complex128),
    RT1: Ref(Complex128),
    RT2: Ref(Complex128),
    EVSCAL: Ref(Complex128),
    CS1: Ref(Complex128),
    SN1: Ref(Complex128)
) -> None: ...

@bind("ZLAEV2")
@external
def zlaev2(
    A: Ref(Complex128),
    B: Ref(Complex128),
    C: Ref(Complex128),
    RT1: Ref(Float64),
    RT2: Ref(Float64),
    CS1: Ref(Float64),
    SN1: Ref(Complex128)
) -> None: ...

@bind("ZLAG2C")
@external
def zlag2c(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    SA: Complex64[LDSA, Flat],
    LDSA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAGS2")
@external
def zlags2(
    UPPER: Ref(Bool),
    A1: Ref(Float64),
    A2: Ref(Complex128),
    A3: Ref(Float64),
    B1: Ref(Float64),
    B2: Ref(Complex128),
    B3: Ref(Float64),
    CSU: Ref(Float64),
    SNU: Ref(Complex128),
    CSV: Ref(Float64),
    SNV: Ref(Complex128),
    CSQ: Ref(Float64),
    SNQ: Ref(Complex128)
) -> None: ...

@bind("ZLAGTM")
@external
def zlagtm(
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    ALPHA: Ref(Float64),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    BETA: Ref(Float64),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("ZLAHEF")
@external
def zlahef(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAHEF_AA")
@external
def zlahef_aa(
    UPLO: Ref(Const(String[1])),
    J1: Ref(Int32),
    M: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLAHEF_RK")
@external
def zlahef_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAHEF_ROOK")
@external
def zlahef_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAHQR")
@external
def zlahqr(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    W: Complex128[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAHR2")
@external
def zlahr2(
    N: Ref(Int32),
    K: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[NB],
    T: Annotated[Complex128[LDT, NB], ORDER_F],
    LDT: Ref(Int32),
    Y: Annotated[Complex128[LDY, NB], ORDER_F],
    LDY: Ref(Int32)
) -> None: ...

@bind("ZLAIC1")
@external
def zlaic1(
    JOB: Ref(Int32),
    J: Ref(Int32),
    X: Complex128[J],
    SEST: Ref(Float64),
    W: Complex128[J],
    GAMMA: Ref(Complex128),
    SESTPR: Ref(Float64),
    S: Ref(Complex128),
    C: Ref(Complex128)
) -> None: ...

@bind("ZLALS0")
@external
def zlals0(
    ICOMPQ: Ref(Int32),
    NL: Ref(Int32),
    NR: Ref(Int32),
    SQRE: Ref(Int32),
    NRHS: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    BX: Complex128[LDBX, Flat],
    LDBX: Ref(Int32),
    PERM: Int32[Flat],
    GIVPTR: Ref(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Ref(Int32),
    POLES: Float64[LDGNUM, Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[LDGNUM, Flat],
    Z: Float64[Flat],
    K: Ref(Int32),
    C: Ref(Float64),
    S: Ref(Float64),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLALSA")
@external
def zlalsa(
    ICOMPQ: Ref(Int32),
    SMLSIZ: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    BX: Complex128[LDBX, Flat],
    LDBX: Ref(Int32),
    U: Float64[LDU, Flat],
    LDU: Ref(Int32),
    VT: Float64[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float64[LDU, Flat],
    DIFR: Float64[LDU, Flat],
    Z: Float64[LDU, Flat],
    POLES: Float64[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ref(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float64[LDU, Flat],
    C: Float64[Flat],
    S: Float64[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLALSD")
@external
def zlalsd(
    UPLO: Ref(Const(String[1])),
    SMLSIZ: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    RCOND: Ref(Float64),
    RANK: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAMSWLQ")
@external
def zlamswlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAMTSQR")
@external
def zlamtsqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLANGB")
@external
def zlangb(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANGE")
@external
def zlange(
    NORM: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANGT")
@external
def zlangt(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat]
) -> Float64: ...

@bind("ZLANHB")
@external
def zlanhb(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHE")
@external
def zlanhe(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHF")
@external
def zlanhf(
    NORM: Ref(Const(String[1])),
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    WORK: Annotated[Float64[Flat], SourceDims("0:*")]
) -> Float64: ...

@bind("ZLANHP")
@external
def zlanhp(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHS")
@external
def zlanhs(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHT")
@external
def zlanht(
    NORM: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Complex128[Flat]
) -> Float64: ...

@bind("ZLANSB")
@external
def zlansb(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANSP")
@external
def zlansp(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANSY")
@external
def zlansy(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANTB")
@external
def zlantb(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANTP")
@external
def zlantp(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANTR")
@external
def zlantr(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLAPLL")
@external
def zlapll(
    N: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    Y: Complex128[Flat],
    INCY: Ref(Int32),
    SSMIN: Ref(Float64)
) -> None: ...

@bind("ZLAPMR")
@external
def zlapmr(
    FORWRD: Ref(Bool),
    M: Ref(Int32),
    N: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("ZLAPMT")
@external
def zlapmt(
    FORWRD: Ref(Bool),
    M: Ref(Int32),
    N: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("ZLAQGB")
@external
def zlaqgb(
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("ZLAQGE")
@external
def zlaqge(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ref(Float64),
    COLCND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("ZLAQHB")
@external
def zlaqhb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("ZLAQHE")
@external
def zlaqhe(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("ZLAQHP")
@external
def zlaqhp(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("ZLAQP2")
@external
def zlaqp2(
    M: Ref(Int32),
    N: Ref(Int32),
    OFFSET: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLAQP2RK")
@external
def zlaqp2rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    IOFFSET: Ref(Int32),
    KMAX: Ref(Int32),
    ABSTOL: Ref(Float64),
    RELTOL: Ref(Float64),
    KP1: Ref(Int32),
    MAXC2NRM: Ref(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    K: Ref(Int32),
    MAXC2NRMK: Ref(Float64),
    RELMAXC2NRMK: Ref(Float64),
    JPIV: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAQP3RK")
@external
def zlaqp3rk(
    M: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    IOFFSET: Ref(Int32),
    NB: Ref(Int32),
    ABSTOL: Ref(Float64),
    RELTOL: Ref(Float64),
    KP1: Ref(Int32),
    MAXC2NRM: Ref(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    DONE: Ref(Bool),
    KB: Ref(Int32),
    MAXC2NRMK: Ref(Float64),
    RELMAXC2NRMK: Ref(Float64),
    JPIV: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Complex128[Flat],
    F: Complex128[LDF, Flat],
    LDF: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAQPS")
@external
def zlaqps(
    M: Ref(Int32),
    N: Ref(Int32),
    OFFSET: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    JPVT: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Complex128[Flat],
    F: Complex128[LDF, Flat],
    LDF: Ref(Int32)
) -> None: ...

@bind("ZLAQR0")
@external
def zlaqr0(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    W: Complex128[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAQR1")
@external
def zlaqr1(
    N: Ref(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    S1: Ref(Complex128),
    S2: Ref(Complex128),
    V: Complex128[Flat]
) -> None: ...

@bind("ZLAQR2")
@external
def zlaqr2(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NW: Ref(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    NS: Ref(Int32),
    ND: Ref(Int32),
    SH: Complex128[Flat],
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    NH: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    NV: Ref(Int32),
    WV: Complex128[LDWV, Flat],
    LDWV: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32)
) -> None: ...

@bind("ZLAQR3")
@external
def zlaqr3(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NW: Ref(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    NS: Ref(Int32),
    ND: Ref(Int32),
    SH: Complex128[Flat],
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    NH: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    NV: Ref(Int32),
    WV: Complex128[LDWV, Flat],
    LDWV: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32)
) -> None: ...

@bind("ZLAQR4")
@external
def zlaqr4(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    W: Complex128[Flat],
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAQR5")
@external
def zlaqr5(
    WANTT: Ref(Bool),
    WANTZ: Ref(Bool),
    KACC22: Ref(Int32),
    N: Ref(Int32),
    KTOP: Ref(Int32),
    KBOT: Ref(Int32),
    NSHFTS: Ref(Int32),
    S: Complex128[Flat],
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    ILOZ: Ref(Int32),
    IHIZ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    U: Complex128[LDU, Flat],
    LDU: Ref(Int32),
    NV: Ref(Int32),
    WV: Complex128[LDWV, Flat],
    LDWV: Ref(Int32),
    NH: Ref(Int32),
    WH: Complex128[LDWH, Flat],
    LDWH: Ref(Int32)
) -> None: ...

@bind("ZLAQSB")
@external
def zlaqsb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("ZLAQSP")
@external
def zlaqsp(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("ZLAQSY")
@external
def zlaqsy(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    EQUED: Ref(Const(String[1]))
) -> None: ...

@bind("ZLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Arg(6), Ref(Arg(7)), Arg(8), Ref(Arg(9)), Arg(10), Arg(11), Arg(12), Ref(Arg(13)), Arg(14), Ref(Arg(15)), Arg(16), Ref(Arg(17)), Arg(18), Ref(Arg(19)), Return('INFO', 1)])
def zlaqz0(
    WANTS: Ref(Const(String[1])),
    WANTQ: Ref(Const(String[1])),
    WANTZ: Ref(Const(String[1])),
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Arg(6), Ref(Arg(7)), Arg(8), Ref(Arg(9)), Ref(Arg(10)), Ref(Arg(11)), Arg(12), Ref(Arg(13)), Ref(Arg(14)), Ref(Arg(15)), Arg(16), Ref(Arg(17))])
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Arg(7), Ref(Arg(8)), Arg(9), Ref(Arg(10)), Arg(11), Ref(Arg(12)), Arg(13), Ref(Arg(14)), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Ref(Arg(18)), Arg(19), Ref(Arg(20)), Arg(21), Ref(Arg(22)), Arg(23), Ref(Arg(24)), Return('INFO', 2)])
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
@native_call([Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4)), Ref(Arg(5)), Ref(Arg(6)), Ref(Arg(7)), Arg(8), Arg(9), Arg(10), Ref(Arg(11)), Arg(12), Ref(Arg(13)), Arg(14), Ref(Arg(15)), Arg(16), Ref(Arg(17)), Arg(18), Ref(Arg(19)), Arg(20), Ref(Arg(21)), Arg(22), Ref(Arg(23)), Return('INFO', 0)])
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
    N: Ref(Int32),
    B1: Ref(Int32),
    BN: Ref(Int32),
    LAMBDA: Ref(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    LD: Float64[Flat],
    LLD: Float64[Flat],
    PIVMIN: Ref(Float64),
    GAPTOL: Ref(Float64),
    Z: Complex128[Flat],
    WANTNC: Ref(Bool),
    NEGCNT: Ref(Int32),
    ZTZ: Ref(Float64),
    MINGMA: Ref(Float64),
    R: Ref(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Ref(Float64),
    RESID: Ref(Float64),
    RQCORR: Ref(Float64),
    WORK: Float64[Flat]
) -> None: ...

@bind("ZLAR2V")
@external
def zlar2v(
    N: Ref(Int32),
    X: Complex128[Flat],
    Y: Complex128[Flat],
    Z: Complex128[Flat],
    INCX: Ref(Int32),
    C: Float64[Flat],
    S: Complex128[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("ZLARCM")
@external
def zlarcm(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    RWORK: Float64[Flat]
) -> None: ...

@bind("ZLARF")
@external
def zlarf(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Complex128[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARF1F")
@external
def zlarf1f(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Complex128[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARF1L")
@external
def zlarf1l(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Complex128[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARFB")
@external
def zlarfb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("ZLARFB_GETT")
@external
def zlarfb_gett(
    IDENT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("ZLARFG")
@external
def zlarfg(
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    TAU: Ref(Complex128)
) -> None: ...

@bind("ZLARFGP")
@external
def zlarfgp(
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    TAU: Ref(Complex128)
) -> None: ...

@bind("ZLARFT")
@external
def zlarft(
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    TAU: Complex128[Flat],
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32)
) -> None: ...

@bind("ZLARFX")
@external
def zlarfx(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    V: Complex128[Flat],
    TAU: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARFY")
@external
def zlarfy(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    V: Complex128[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARGV")
@external
def zlargv(
    N: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    Y: Complex128[Flat],
    INCY: Ref(Int32),
    C: Float64[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("ZLARNV")
@external
def zlarnv(
    IDIST: Ref(Int32),
    ISEED: Int32[4],
    N: Ref(Int32),
    X: Complex128[Flat]
) -> None: ...

@bind("ZLARRV")
@external
def zlarrv(
    N: Ref(Int32),
    VL: Ref(Float64),
    VU: Ref(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    PIVMIN: Ref(Float64),
    ISPLIT: Int32[Flat],
    M: Ref(Int32),
    DOL: Ref(Int32),
    DOU: Ref(Int32),
    MINRGP: Ref(Float64),
    RTOL1: Ref(Float64),
    RTOL2: Ref(Float64),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WGAP: Float64[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLARSCL2")
@external
def zlarscl2(
    M: Ref(Int32),
    N: Ref(Int32),
    D: Float64[Flat],
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32)
) -> None: ...

@bind("ZLARTG")
@external
def zlartg(
    f: Ref(Complex128),
    g: Ref(Complex128),
    c: Ref(Float64),
    s: Ref(Complex128),
    r: Ref(Complex128)
) -> None: ...

@bind("ZLARTV")
@external
def zlartv(
    N: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    Y: Complex128[Flat],
    INCY: Ref(Int32),
    C: Float64[Flat],
    S: Complex128[Flat],
    INCC: Ref(Int32)
) -> None: ...

@bind("ZLARZ")
@external
def zlarz(
    SIDE: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    V: Complex128[Flat],
    INCV: Ref(Int32),
    TAU: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARZB")
@external
def zlarzb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("ZLARZT")
@external
def zlarzt(
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    TAU: Complex128[Flat],
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32)
) -> None: ...

@bind("ZLASCL")
@external
def zlascl(
    TYPE: Ref(Const(String[1])),
    KL: Ref(Int32),
    KU: Ref(Int32),
    CFROM: Ref(Float64),
    CTO: Ref(Float64),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLASCL2")
@external
def zlascl2(
    M: Ref(Int32),
    N: Ref(Int32),
    D: Float64[Flat],
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32)
) -> None: ...

@bind("ZLASET")
@external
def zlaset(
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    BETA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("ZLASR")
@external
def zlasr(
    SIDE: Ref(Const(String[1])),
    PIVOT: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("ZLASSQ")
@external
def zlassq(
    n: Ref(Int32),
    x: Complex128[Flat],
    incx: Ref(Int32),
    scale: Ref(Float64),
    sumsq: Ref(Float64)
) -> None: ...

@bind("ZLASWLQ")
@external
def zlaswlq(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLASWP")
@external
def zlaswp(
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    K1: Ref(Int32),
    K2: Ref(Int32),
    IPIV: Int32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZLASYF")
@external
def zlasyf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLASYF_AA")
@external
def zlasyf_aa(
    UPLO: Ref(Const(String[1])),
    J1: Ref(Int32),
    M: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    H: Complex128[LDH, Flat],
    LDH: Ref(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLASYF_RK")
@external
def zlasyf_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLASYF_ROOK")
@external
def zlasyf_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    KB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAT2C")
@external
def zlat2c(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    SA: Complex64[LDSA, Flat],
    LDSA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLATBS")
@external
def zlatbs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    X: Complex128[Flat],
    SCALE: Ref(Float64),
    CNORM: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLATDF")
@external
def zlatdf(
    IJOB: Ref(Int32),
    N: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    RHS: Complex128[Flat],
    RDSUM: Ref(Float64),
    RDSCAL: Ref(Float64),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("ZLATPS")
@external
def zlatps(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    SCALE: Ref(Float64),
    CNORM: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLATRD")
@external
def zlatrd(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Float64[Flat],
    TAU: Complex128[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ref(Int32)
) -> None: ...

@bind("ZLATRS")
@external
def zlatrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    SCALE: Ref(Float64),
    CNORM: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLATRS3")
@external
def zlatrs3(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    NORMIN: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    SCALE: Float64[Flat],
    CNORM: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLATRZ")
@external
def zlatrz(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLATSQR")
@external
def zlatsqr(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAUNHR_COL_GETRFNP")
@external
def zlaunhr_col_getrfnp(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    D: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAUNHR_COL_GETRFNP2")
@external
def zlaunhr_col_getrfnp2(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    D: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAUU2")
@external
def zlauu2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZLAUUM")
@external
def zlauum(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPBCON")
@external
def zpbcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPBEQU")
@external
def zpbequ(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPBRFS")
@external
def zpbrfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPBSTF")
@external
def zpbstf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPBSV")
@external
def zpbsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPBSVX")
@external
def zpbsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPBTF2")
@external
def zpbtf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPBTRF")
@external
def zpbtrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPBTRS")
@external
def zpbtrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPFTRF")
@external
def zpftrf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPFTRI")
@external
def zpftri(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPFTRS")
@external
def zpftrs(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOCON")
@external
def zpocon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOEQU")
@external
def zpoequ(
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOEQUB")
@external
def zpoequb(
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPORFS")
@external
def zporfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPORFSX")
@external
def zporfsx(
    UPLO: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOSV")
@external
def zposv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOSVX")
@external
def zposvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOSVXX")
@external
def zposvxx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    RPVGRW: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOTF2")
@external
def zpotf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOTRF")
@external
def zpotrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOTRF2")
@external
def zpotrf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOTRI")
@external
def zpotri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPOTRS")
@external
def zpotrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPPCON")
@external
def zppcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPPEQU")
@external
def zppequ(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPPRFS")
@external
def zpprfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPPSV")
@external
def zppsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPPSVX")
@external
def zppsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPPTRF")
@external
def zpptrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPPTRI")
@external
def zpptri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPPTRS")
@external
def zpptrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPSTF2")
@external
def zpstf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    PIV: Int32[N],
    RANK: Ref(Int32),
    TOL: Ref(Float64),
    WORK: Float64[2 * N],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPSTRF")
@external
def zpstrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    PIV: Int32[N],
    RANK: Ref(Int32),
    TOL: Ref(Float64),
    WORK: Float64[2 * N],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPTCON")
@external
def zptcon(
    N: Ref(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPTEQR")
@external
def zpteqr(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPTRFS")
@external
def zptrfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    DF: Float64[Flat],
    EF: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPTSV")
@external
def zptsv(
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPTSVX")
@external
def zptsvx(
    FACT: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    DF: Float64[Flat],
    EF: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPTTRF")
@external
def zpttrf(
    N: Ref(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPTTRS")
@external
def zpttrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZPTTS2")
@external
def zptts2(
    IUPLO: Ref(Int32),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("ZROT")
@external
def zrot(
    N: Ref(Int32),
    CX: Complex128[Flat],
    INCX: Ref(Int32),
    CY: Complex128[Flat],
    INCY: Ref(Int32),
    C: Ref(Float64),
    S: Ref(Complex128)
) -> None: ...

@bind("ZRSCL")
@external
def zrscl(
    N: Ref(Int32),
    A: Ref(Complex128),
    X: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZSPCON")
@external
def zspcon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSPMV")
@external
def zspmv(
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

@bind("ZSPR")
@external
def zspr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    AP: Complex128[Flat]
) -> None: ...

@bind("ZSPRFS")
@external
def zsprfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSPSV")
@external
def zspsv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSPSVX")
@external
def zspsvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSPTRF")
@external
def zsptrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSPTRI")
@external
def zsptri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSPTRS")
@external
def zsptrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSTEDC")
@external
def zstedc(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSTEGR")
@external
def zstegr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    ABSTOL: Ref(Float64),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSTEIN")
@external
def zstein(
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    M: Ref(Int32),
    W: Float64[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSTEMR")
@external
def zstemr(
    JOBZ: Ref(Const(String[1])),
    RANGE: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ref(Float64),
    VU: Ref(Float64),
    IL: Ref(Int32),
    IU: Ref(Int32),
    M: Ref(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    NZC: Ref(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Ref(Bool),
    WORK: Float64[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSTEQR")
@external
def zsteqr(
    COMPZ: Ref(Const(String[1])),
    N: Ref(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    WORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYCON")
@external
def zsycon(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYCON_3")
@external
def zsycon_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYCON_ROOK")
@external
def zsycon_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    ANORM: Ref(Float64),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYCONV")
@external
def zsyconv(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    E: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYCONVF")
@external
def zsyconvf(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYCONVF_ROOK")
@external
def zsyconvf_rook(
    UPLO: Ref(Const(String[1])),
    WAY: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYEQUB")
@external
def zsyequb(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    S: Float64[Flat],
    SCOND: Ref(Float64),
    AMAX: Ref(Float64),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYMV")
@external
def zsymv(
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

@bind("ZSYR")
@external
def zsyr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("ZSYRFS")
@external
def zsyrfs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYRFSX")
@external
def zsyrfsx(
    UPLO: Ref(Const(String[1])),
    EQUED: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYSV")
@external
def zsysv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYSV_AA")
@external
def zsysv_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYSV_AA_2STAGE")
@external
def zsysv_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex128[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYSV_RK")
@external
def zsysv_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYSV_ROOK")
@external
def zsysv_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYSVX")
@external
def zsysvx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYSVXX")
@external
def zsysvxx(
    FACT: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ref(Int32),
    IPIV: Int32[Flat],
    EQUED: Ref(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    RCOND: Ref(Float64),
    RPVGRW: Ref(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ref(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ref(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYSWAPR")
@external
def zsyswapr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    I1: Ref(Int32),
    I2: Ref(Int32)
) -> None: ...

@bind("ZSYTF2")
@external
def zsytf2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTF2_RK")
@external
def zsytf2_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTF2_ROOK")
@external
def zsytf2_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRF")
@external
def zsytrf(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRF_AA")
@external
def zsytrf_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRF_AA_2STAGE")
@external
def zsytrf_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex128[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRF_RK")
@external
def zsytrf_rk(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRF_ROOK")
@external
def zsytrf_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRI")
@external
def zsytri(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRI2")
@external
def zsytri2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRI2X")
@external
def zsytri2x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRI_3")
@external
def zsytri_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRI_3X")
@external
def zsytri_3x(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRI_ROOK")
@external
def zsytri_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRS")
@external
def zsytrs(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRS2")
@external
def zsytrs2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRS_3")
@external
def zsytrs_3(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRS_AA")
@external
def zsytrs_aa(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRS_AA_2STAGE")
@external
def zsytrs_aa_2stage(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TB: Complex128[Flat],
    LTB: Ref(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZSYTRS_ROOK")
@external
def zsytrs_rook(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTBCON")
@external
def ztbcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTBRFS")
@external
def ztbrfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTBTRS")
@external
def ztbtrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    KD: Ref(Int32),
    NRHS: Ref(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTFSM")
@external
def ztfsm(
    TRANSR: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    B: Annotated[Complex128[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Ref(Int32)
) -> None: ...

@bind("ZTFTRI")
@external
def ztftri(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTFTTP")
@external
def ztfttp(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    AP: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTFTTR")
@external
def ztfttr(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    A: Annotated[Complex128[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTGEVC")
@external
def ztgevc(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    S: Complex128[LDS, Flat],
    LDS: Ref(Int32),
    P: Complex128[LDP, Flat],
    LDP: Ref(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTGEX2")
@external
def ztgex2(
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    J1: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTGEXC")
@external
def ztgexc(
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    IFST: Ref(Int32),
    ILST: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTGSEN")
@external
def ztgsen(
    IJOB: Ref(Int32),
    WANTQ: Ref(Bool),
    WANTZ: Ref(Bool),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ref(Int32),
    M: Ref(Int32),
    PL: Ref(Float64),
    PR: Ref(Float64),
    DIF: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTGSJA")
@external
def ztgsja(
    JOBU: Ref(Const(String[1])),
    JOBV: Ref(Const(String[1])),
    JOBQ: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    TOLA: Ref(Float64),
    TOLB: Ref(Float64),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Complex128[Flat],
    NCYCLE: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTGSNA")
@external
def ztgsna(
    JOB: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    S: Float64[Flat],
    DIF: Float64[Flat],
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTGSY2")
@external
def ztgsy2(
    TRANS: Ref(Const(String[1])),
    IJOB: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    D: Complex128[LDD, Flat],
    LDD: Ref(Int32),
    E: Complex128[LDE, Flat],
    LDE: Ref(Int32),
    F: Complex128[LDF, Flat],
    LDF: Ref(Int32),
    SCALE: Ref(Float64),
    RDSUM: Ref(Float64),
    RDSCAL: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTGSYL")
@external
def ztgsyl(
    TRANS: Ref(Const(String[1])),
    IJOB: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    D: Complex128[LDD, Flat],
    LDD: Ref(Int32),
    E: Complex128[LDE, Flat],
    LDE: Ref(Int32),
    F: Complex128[LDF, Flat],
    LDF: Ref(Int32),
    SCALE: Ref(Float64),
    DIF: Ref(Float64),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPCON")
@external
def ztpcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPLQT")
@external
def ztplqt(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    MB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPLQT2")
@external
def ztplqt2(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPMLQT")
@external
def ztpmlqt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    MB: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPMQRT")
@external
def ztpmqrt(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    NB: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPQRT")
@external
def ztpqrt(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPQRT2")
@external
def ztpqrt2(
    M: Ref(Int32),
    N: Ref(Int32),
    L: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPRFB")
@external
def ztprfb(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIRECT: Ref(Const(String[1])),
    STOREV: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Ref(Int32)
) -> None: ...

@bind("ZTPRFS")
@external
def ztprfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPTRI")
@external
def ztptri(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPTRS")
@external
def ztptrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPTTF")
@external
def ztpttf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Annotated[Complex128[Flat], SourceDims("0:*")],
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTPTTR")
@external
def ztpttr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRCON")
@external
def ztrcon(
    NORM: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    RCOND: Ref(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTREVC")
@external
def ztrevc(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTREVC3")
@external
def ztrevc3(
    SIDE: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTREXC")
@external
def ztrexc(
    COMPQ: Ref(Const(String[1])),
    N: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    IFST: Ref(Int32),
    ILST: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRRFS")
@external
def ztrrfs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ref(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRSEN")
@external
def ztrsen(
    JOB: Ref(Const(String[1])),
    COMPQ: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    W: Complex128[Flat],
    M: Ref(Int32),
    S: Ref(Float64),
    SEP: Ref(Float64),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRSNA")
@external
def ztrsna(
    JOB: Ref(Const(String[1])),
    HOWMNY: Ref(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Ref(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ref(Int32),
    S: Float64[Flat],
    SEP: Float64[Flat],
    MM: Ref(Int32),
    M: Ref(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Ref(Int32),
    RWORK: Float64[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRSYL")
@external
def ztrsyl(
    TRANA: Ref(Const(String[1])),
    TRANB: Ref(Const(String[1])),
    ISGN: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    SCALE: Ref(Float64),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRSYL3")
@external
def ztrsyl3(
    TRANA: Ref(Const(String[1])),
    TRANB: Ref(Const(String[1])),
    ISGN: Ref(Int32),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    SCALE: Ref(Float64),
    SWORK: Float64[LDSWORK, Flat],
    LDSWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRTI2")
@external
def ztrti2(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRTRI")
@external
def ztrtri(
    UPLO: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRTRS")
@external
def ztrtrs(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    NRHS: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRTTF")
@external
def ztrttf(
    TRANSR: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Annotated[Complex128[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ref(Int32),
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTRTTP")
@external
def ztrttp(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    AP: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZTZRZF")
@external
def ztzrzf(
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNBDB")
@external
def zunbdb(
    TRANS: Ref(Const(String[1])),
    SIGNS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ref(Int32),
    X12: Complex128[LDX12, Flat],
    LDX12: Ref(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ref(Int32),
    X22: Complex128[LDX22, Flat],
    LDX22: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    TAUQ2: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNBDB1")
@external
def zunbdb1(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNBDB2")
@external
def zunbdb2(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNBDB3")
@external
def zunbdb3(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNBDB4")
@external
def zunbdb4(
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    PHANTOM: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNBDB5")
@external
def zunbdb5(
    M1: Ref(Int32),
    M2: Ref(Int32),
    N: Ref(Int32),
    X1: Complex128[Flat],
    INCX1: Ref(Int32),
    X2: Complex128[Flat],
    INCX2: Ref(Int32),
    Q1: Complex128[LDQ1, Flat],
    LDQ1: Ref(Int32),
    Q2: Complex128[LDQ2, Flat],
    LDQ2: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNBDB6")
@external
def zunbdb6(
    M1: Ref(Int32),
    M2: Ref(Int32),
    N: Ref(Int32),
    X1: Complex128[Flat],
    INCX1: Ref(Int32),
    X2: Complex128[Flat],
    INCX2: Ref(Int32),
    Q1: Complex128[LDQ1, Flat],
    LDQ1: Ref(Int32),
    Q2: Complex128[LDQ2, Flat],
    LDQ2: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNCSD")
@external
def zuncsd(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    JOBV2T: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    SIGNS: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ref(Int32),
    X12: Complex128[LDX12, Flat],
    LDX12: Ref(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ref(Int32),
    X22: Complex128[LDX22, Flat],
    LDX22: Ref(Int32),
    THETA: Float64[Flat],
    U1: Complex128[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Complex128[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Complex128[LDV1T, Flat],
    LDV1T: Ref(Int32),
    V2T: Complex128[LDV2T, Flat],
    LDV2T: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNCSD2BY1")
@external
def zuncsd2by1(
    JOBU1: Ref(Const(String[1])),
    JOBU2: Ref(Const(String[1])),
    JOBV1T: Ref(Const(String[1])),
    M: Ref(Int32),
    P: Ref(Int32),
    Q: Ref(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ref(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ref(Int32),
    THETA: Float64[Flat],
    U1: Complex128[LDU1, Flat],
    LDU1: Ref(Int32),
    U2: Complex128[LDU2, Flat],
    LDU2: Ref(Int32),
    V1T: Complex128[LDV1T, Flat],
    LDV1T: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ref(Int32),
    IWORK: Int32[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNG2L")
@external
def zung2l(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNG2R")
@external
def zung2r(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGBR")
@external
def zungbr(
    VECT: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGHR")
@external
def zunghr(
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGL2")
@external
def zungl2(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGLQ")
@external
def zunglq(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGQL")
@external
def zungql(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGQR")
@external
def zungqr(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGR2")
@external
def zungr2(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGRQ")
@external
def zungrq(
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGTR")
@external
def zungtr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGTSQR")
@external
def zungtsqr(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNGTSQR_ROW")
@external
def zungtsqr_row(
    M: Ref(Int32),
    N: Ref(Int32),
    MB: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNHR_COL")
@external
def zunhr_col(
    M: Ref(Int32),
    N: Ref(Int32),
    NB: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ref(Int32),
    D: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNM22")
@external
def zunm22(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    N1: Ref(Int32),
    N2: Ref(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNM2L")
@external
def zunm2l(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNM2R")
@external
def zunm2r(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNMBR")
@external
def zunmbr(
    VECT: Ref(Const(String[1])),
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNMHR")
@external
def zunmhr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ILO: Ref(Int32),
    IHI: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNML2")
@external
def zunml2(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNMLQ")
@external
def zunmlq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNMQL")
@external
def zunmql(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNMQR")
@external
def zunmqr(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNMR2")
@external
def zunmr2(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNMR3")
@external
def zunmr3(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNMRQ")
@external
def zunmrq(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNMRZ")
@external
def zunmrz(
    SIDE: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    L: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUNMTR")
@external
def zunmtr(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    LWORK: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUPGTR")
@external
def zupgtr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    TAU: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...

@bind("ZUPMTR")
@external
def zupmtr(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    AP: Complex128[Flat],
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32),
    WORK: Complex128[Flat],
    INFO: Ref(Int32)
) -> None: ...
