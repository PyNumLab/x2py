@external
@native_call([Addr(Arg(0))])
def add_one(
    value: Annotated[Int32, Intent('inout')]
) -> Int32: ...
