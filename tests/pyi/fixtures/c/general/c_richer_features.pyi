class x2py_status(Enum[Int]):
    pass

class x2py_flags(CStruct):
    ready: UInt32
    mode: UInt32
    reserved: UInt32

class x2py_context(CStruct, Opaque):
    pass

class x2py_scalar(CUnion):
    i32: Int
    u64: UInt64
    f64: Float64

X2PY_STATUS_OK: Final[x2py_status] = 0

X2PY_STATUS_RETRY: Final[x2py_status] = 1

X2PY_STATUS_ERROR: Final[x2py_status] = -1

def x2py_slow_path() -> Int: ...

def x2py_sort(
    items: Ptr(Any),
    count: SizeT,
    item_size: SizeT,
    compare: CFunctionPointer
) -> Int: ...

def x2py_register_callback(
    context: Ptr(x2py_context),
    callback: CFunctionPointer,
    userdata: Ptr(Any)
) -> Int: ...

def x2py_status_message(
    status: x2py_status
) -> Ptr(Const(Int8)): ...

def x2py_fill_matrix(
    rows: SizeT,
    cols: SizeT,
    matrix: Float64[rows, cols]
) -> None: ...
