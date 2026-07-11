from x2py.contracts import Addr, Allocatable, Arg, Float64, Int32, Returns, native_call

@native_call([Arg(0), Addr(Arg(1))])
def replace_values(
    values: Allocatable[Float64[:]],
    mode: Int32
) -> Returns["values", Allocatable[Float64[:]]]: ...
