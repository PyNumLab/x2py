@native_call([Arg(0), Arg(1)])
def replace_values(
    values: Annotated[Float64[:], Allocatable],
    mode: Ptr(Const(Int32))
) -> Returns["values", Annotated[Float64[:], Allocatable], Optional]: ...
