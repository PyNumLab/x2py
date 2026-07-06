from x2py.contracts import Addr, Allocatable, Annotated, Arg, Float64, Int32, Returns, native_call

@native_call([Arg(0), Addr(Arg(1))])
def replace_values(
    values: Annotated[Float64[:], Allocatable] | None,
    mode: Int32
) -> Returns["values", Annotated[Float64[:], Allocatable]] | None: ...
