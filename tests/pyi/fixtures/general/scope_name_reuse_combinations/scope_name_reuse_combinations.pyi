class same_name:
    def __init__(
        self,
        *,
        payload: Int32 = ...
    ) -> None: ...

    payload: Int32

@module_variable("same_name_i", access="get")
def get_same_name_i() -> Int32: ...

@module_variable("same_name_i", access="set")
def set_same_name_i(value: Int32) -> None: ...

@module_variable("same_name_r", access="get")
def get_same_name_r() -> Float32: ...

@module_variable("same_name_r", access="set")
def set_same_name_r(value: Float32) -> None: ...

@module_variable("same_name_l", access="get")
def get_same_name_l() -> Bool: ...

@module_variable("same_name_l", access="set")
def set_same_name_l(value: Bool) -> None: ...

@module_variable("same_name_c", access="get")
def get_same_name_c() -> Complex64: ...

@module_variable("same_name_c", access="set")
def set_same_name_c(value: Complex64) -> None: ...

same_name_s: Annotated[String, FortranCharacterLength("8")]

def do_work_i(
    same_name: Ptr(Int32)
) -> None: ...

def do_work_r(
    same_name: Ptr(Const(Float32))
) -> None: ...

def do_work_l(
    same_name: Ptr(Const(Bool))
) -> None: ...

def host_one(
    same_name: Ptr(Int32)
) -> None: ...

def host_two(
    same_name: Ptr(Float32)
) -> None: ...

def convert_to_complex(
    same_name: Ptr(Const(Int32))
) -> Complex64: ...

def convert_to_char(
    same_name: Ptr(Const(Float32))
) -> Annotated[String, FortranCharacterLength("16")]: ...

def convert_to_logical(
    same_name: Annotated[Ptr(Const(String)), FortranCharacterLength("*")]
) -> Bool: ...

@overload("do_work_i")
def do_work(
    same_name: Ptr(Int32)
) -> None: ...

@overload("do_work_r")
def do_work(
    same_name: Ptr(Const(Float32))
) -> None: ...

@overload("do_work_l")
def do_work(
    same_name: Ptr(Const(Bool))
) -> None: ...
