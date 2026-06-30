@external
@native_call([Ref(Arg(0))])
def triple_value(
    value: Const(Int32)
) -> Int32: ...

@external
@native_call([Ref(Arg(0))])
def offset_value(
    value: Const(Int32)
) -> Int32: ...
