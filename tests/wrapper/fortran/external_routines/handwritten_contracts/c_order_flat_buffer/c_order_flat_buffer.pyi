from typing import Annotated
from x2py.typing import Flat, Float64, Int32, ORDER_C, Addr, external

@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def row_sums_c(
    n: Int32,
    values: Annotated[Float64[Flat, 3], ORDER_C],
    result: Float64[Flat],
) -> None: ...
