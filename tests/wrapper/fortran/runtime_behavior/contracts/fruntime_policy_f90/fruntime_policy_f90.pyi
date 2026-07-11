from x2py.contracts import Addr, Arg, Int32, Return, String, native_call

def pause_for_one_second() -> None: ...

def pause_with_gil() -> None: ...

@native_call([Addr(Arg(0)), Return('status', 0), Return('message', 1)])
def solve(
    value: Int32
) -> tuple[Int32, String[32]]: ...
