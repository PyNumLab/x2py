class same_name:
    payload: Int32

same_name_i: Int32

same_name_r: Float64

same_name_l: Bool

same_name_c: Unknown

same_name_s: Unknown

@call_map(NativeArg('same_name', 0, source='arg', position=0, result=0, intent='inout'))
def do_work_i(
    same_name: Int32
) -> Returns["same_name", Int32]: ...

def do_work_r(
    same_name: Float64
) -> None: ...

def do_work_l(
    same_name: Bool
) -> None: ...

@call_map(NativeArg('same_name', 0, source='arg', position=0, result=0, intent='inout'))
def host_one(
    same_name: Int32
) -> Returns["same_name", Int32]: ...

@call_map(NativeArg('same_name', 0, source='arg', position=0, result=0, intent='inout'))
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
