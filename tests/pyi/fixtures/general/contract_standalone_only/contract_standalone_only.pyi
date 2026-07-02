@external
def standalone_ping() -> None: ...

@external
@native_call([Ref(Arg(0))])
def standalone_double(
    value: Const(Int32)
) -> Int32: ...
