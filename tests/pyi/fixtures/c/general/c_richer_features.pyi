class x2py_flags:
    ready: UInt32
    mode: UInt32
    reserved: UInt32

class x2py_context(Opaque):
    pass

class x2py_scalar:
    i32: Int32
    u64: UInt64
    f64: Float64

X2PY_STATUS_OK: Final[Int32]

X2PY_STATUS_RETRY: Final[Int32]

X2PY_STATUS_ERROR: Final[Int32]

def x2py_fast_path() -> Int32: ...

def x2py_slow_path() -> Int32: ...

def x2py_register_callback(
    context: Ptr(x2py_context),
    callback: CFunctionPointer,
    userdata: Ptr(Any)
) -> Int32: ...

def x2py_status_message(
    status: Int32
) -> Ptr(Const(Int8)): ...

def x2py_fill_matrix(
    rows: SizeT,
    cols: SizeT,
    matrix: Float64[rows, cols]
) -> None: ...
