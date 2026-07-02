from first_math import add_one

@native_call([Ref(Arg(0))])
def double_after_add(
    value: Const(Int32)
) -> Int32: ...
