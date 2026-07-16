from x2py.contracts import Final, Float32, Int32

n0: Final[Int32] = 4

n1: Final[Int32] = 6

def use_expr(
    x: Int32[n1],
    y: Float32[n0 * 2]
) -> None: ...
