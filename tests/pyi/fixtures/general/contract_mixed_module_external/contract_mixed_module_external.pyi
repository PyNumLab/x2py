from . import contract_math_mod

@external
def external_double(
    value: Ptr(Const(Int32))
) -> Int32: ...
