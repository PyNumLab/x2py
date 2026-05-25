class same_name:
    payload: Int32

same_name_i: Int32

same_name_r: Float64

same_name_l: Bool

same_name_c: Complex128

same_name_s: String

def do_work_i(
    same_name: Ptr(Int32)
) -> None: ...

def do_work_r(
    same_name: Ptr(Const(Float64))
) -> None: ...

def do_work_l(
    same_name: Ptr(Const(Bool))
) -> None: ...

def host_one(
    same_name: Ptr(Int32)
) -> None: ...

def host_two(
    same_name: Ptr(Float64)
) -> None: ...

def convert_to_complex(
    same_name: Ptr(Const(Int32))
) -> Complex128: ...

def convert_to_char(
    same_name: Ptr(Const(Float64))
) -> String: ...

def convert_to_logical(
    same_name: Ptr(Const(String))
) -> Bool: ...
