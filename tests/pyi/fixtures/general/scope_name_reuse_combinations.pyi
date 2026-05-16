class same_name:
    payload: Int32

same_name_i: Int32

same_name_r: Float64

same_name_l: Bool

same_name_c: Unknown

same_name_s: Unknown

def do_work_i(
    same_name: Int32
) -> Returns["same_name", Int32]: ...

def do_work_r(
    same_name: Float64
) -> None: ...

def do_work_l(
    same_name: Bool
) -> None: ...

def host_one(
    same_name: Int32
) -> Returns["same_name", Int32]: ...

def host_two(
    same_name: Float64
) -> Returns["same_name", Float64]: ...

def convert_to_complex(
    same_name: Int32
) -> Unknown: ...

def convert_to_char(
    same_name: Float64
) -> Unknown: ...

def convert_to_logical(
    same_name: Unknown
) -> Bool: ...
