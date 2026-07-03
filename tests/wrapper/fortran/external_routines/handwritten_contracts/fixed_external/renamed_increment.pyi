@external
@bind("fixed_add")
@native_call([Addr(Arg(0))])
def renamed_increment(value: Annotated[Int32, Intent("inout")]) -> Int32: ...
