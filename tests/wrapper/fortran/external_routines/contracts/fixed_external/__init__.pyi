from x2py.contracts import Addr, Arg, Int32, external, native_call

@external
@native_call([Addr(Arg(0))])
def fixed_add(
    value: Int32
) -> Int32: ...
