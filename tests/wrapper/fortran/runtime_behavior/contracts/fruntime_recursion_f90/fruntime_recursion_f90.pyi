@native_call([Addr(Arg(0))])
def factorial(
    n: Const(Int32)
) -> Int32: ...

@native_call([Addr(Arg(0))])
def add_one(
    n: Const(Int32)
) -> Int32: ...
