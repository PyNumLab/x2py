from first_math import add_one

@native_call([Addr(Arg(0))])
def double_after_add(
    value: Int32
) -> Int32: ...
