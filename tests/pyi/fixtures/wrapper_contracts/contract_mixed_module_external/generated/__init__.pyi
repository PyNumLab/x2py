from . import contract_math_mod

@external
@native_call([Ref(Arg(0))])
def external_double(
    value: Const(Int32)
) -> Int32: ...
