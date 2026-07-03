from typing import Annotated
from x2py.typing import Flat, Float64, Int32, Intent, ORDER_C, Addr, external

@external
def row_sums_c(
    n: Addr(Int32),
    values: Annotated[Float64[Flat, 3], ORDER_C],
    result: Annotated[Float64[Flat], Intent("out")],
) -> None: ...
