@external
@native_call([Addr(Arg(0))])
def fixed_add(
    value: Annotated[Int32, Intent('inout')]
) -> Int32: ...
