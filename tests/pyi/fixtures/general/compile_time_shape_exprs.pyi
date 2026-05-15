n0: Int32

n1: Int32

def use_expr(
    x: Int32[Shape('0:n1-1'), FortranContiguous],
    y: Float64[Shape('1:n0*2'), FortranContiguous]
) -> None: ...
