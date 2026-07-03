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

@native_call([Addr(Arg(0))])
def do_work_i(
    same_name: Annotated[Int32, Intent('inout')]
) -> None: ...

@native_call([Addr(Arg(0))])
def do_work_r(
    same_name: Const(Float32)
) -> None: ...

@native_call([Addr(Arg(0))])
def do_work_l(
    same_name: Const(Bool)
) -> None: ...

@native_call([Addr(Arg(0))])
def host_one(
    same_name: Annotated[Int32, Intent('inout')]
) -> None: ...

@native_call([Addr(Arg(0))])
def host_two(
    same_name: Annotated[Float32, Intent('inout')]
) -> None: ...

@native_call([Addr(Arg(0))])
def convert_to_complex(
    same_name: Const(Int32)
) -> Complex64: ...

@native_call([Addr(Arg(0))])
def convert_to_char(
    same_name: Const(Float32)
) -> String[16]: ...

def convert_to_logical(
    same_name: Const(String)
) -> Bool: ...

@overload("do_work_i")
@native_call([Addr(Arg(0))])
def do_work(
    same_name: Annotated[Int32, Intent('inout')]
) -> None: ...

@overload("do_work_r")
@native_call([Addr(Arg(0))])
def do_work(
    same_name: Const(Float32)
) -> None: ...

@overload("do_work_l")
@native_call([Addr(Arg(0))])
def do_work(
    same_name: Const(Bool)
) -> None: ...
