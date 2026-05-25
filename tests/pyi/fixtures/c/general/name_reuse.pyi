class same_name:
    payload: Int32

same_name_i: Int32

same_name_r: Float32

same_name_l: Bool

same_name_c: Complex128

same_name_s: Int8[8]

def do_work_i(
    same_name: Ptr(Int32)
) -> None: ...

def do_work_r(
    same_name: Float32
) -> None: ...

def do_work_l(
    same_name: Bool,
    shared: Ptr(same_name)
) -> None: ...

def convert_to_complex(
    same_name: Int32
) -> Complex128: ...

def convert_to_string(
    same_name: Float32,
    shared: Int8[16]
) -> Int32: ...

def convert_to_logical(
    same_name: Ptr(Const(Int8))
) -> Bool: ...
