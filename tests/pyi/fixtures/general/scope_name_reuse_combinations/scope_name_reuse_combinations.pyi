class same_name:
    def __init__(
        self,
        *,
        payload: Int32 = ...
    ) -> None: ...

    payload: Int32

same_name_i: Int32

same_name_r: Float32

same_name_l: Bool

same_name_c: Complex64

same_name_s: String[8]

def do_work_i(
    same_name: Ref(Int32)
) -> None: ...

@native_call([Ref(Arg(0))])
def do_work_r(
    same_name: Const(Float32)
) -> None: ...

@native_call([Ref(Arg(0))])
def do_work_l(
    same_name: Const(Bool)
) -> None: ...

def host_one(
    same_name: Ref(Int32)
) -> None: ...

def host_two(
    same_name: Ref(Float32)
) -> None: ...

@native_call([Ref(Arg(0))])
def convert_to_complex(
    same_name: Const(Int32)
) -> Complex64: ...

@native_call([Ref(Arg(0))])
def convert_to_char(
    same_name: Const(Float32)
) -> String[16]: ...

def convert_to_logical(
    same_name: Ref(Const(String))
) -> Bool: ...

@overload("do_work_i")
def do_work(
    same_name: Ref(Int32)
) -> None: ...

@overload("do_work_r")
@native_call([Ref(Arg(0))])
def do_work(
    same_name: Const(Float32)
) -> None: ...

@overload("do_work_l")
@native_call([Ref(Arg(0))])
def do_work(
    same_name: Const(Bool)
) -> None: ...
