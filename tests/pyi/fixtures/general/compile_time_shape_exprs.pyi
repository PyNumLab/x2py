n0: Int32

n1: Int32

def use_expr(
    x: Int32[Shape('0:n1-1'), ORDER_F],
    y: Float64[Shape('1:n0*2'), ORDER_F]
) -> tuple[Returns["x", Int32[Shape('0:n1-1'), ORDER_F]], Returns["y", Float64[Shape('1:n0*2'), ORDER_F]]]: ...
