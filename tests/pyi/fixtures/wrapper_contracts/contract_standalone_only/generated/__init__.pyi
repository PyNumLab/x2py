@external
def standalone_ping() -> None: ...

@external
def standalone_double(
    value: Ptr(Const(Int32))
) -> Int32: ...
