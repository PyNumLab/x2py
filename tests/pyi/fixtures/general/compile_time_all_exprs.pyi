a: Final[Int32]

b: Final[Int32]

c: Final[Int32]

p_add: Final[Int32]

p_sub: Final[Int32]

p_mul: Final[Int32]

p_div: Final[Int32]

p_pow: Final[Int32]

p_mix: Final[Int32]

def all_exprs(
    x1: Int32[Shape('1:p_add'), ORDER_F],
    x2: Int32[Shape('1:p_sub'), ORDER_F],
    x3: Int32[Shape('1:p_mul'), ORDER_F],
    x4: Int32[Shape('1:p_div'), ORDER_F],
    x5: Int32[Shape('1:p_pow'), ORDER_F],
    x6: Int32[Shape('0:p_mix'), ORDER_F],
    x7: Int32[Shape('1:-(-a + b)'), ORDER_F],
    x8: Int32[Shape('1:(a+b)*(c+1)-1'), ORDER_F],
    x9: Int32[Shape('1:(a-b)*(a-c)'), ORDER_F]
) -> tuple[Returns["x1", Int32[Shape('1:p_add'), ORDER_F]], Returns["x2", Int32[Shape('1:p_sub'), ORDER_F]], Returns["x3", Int32[Shape('1:p_mul'), ORDER_F]], Returns["x4", Int32[Shape('1:p_div'), ORDER_F]], Returns["x5", Int32[Shape('1:p_pow'), ORDER_F]], Returns["x6", Int32[Shape('0:p_mix'), ORDER_F]], Returns["x7", Int32[Shape('1:-(-a + b)'), ORDER_F]], Returns["x8", Int32[Shape('1:(a+b)*(c+1)-1'), ORDER_F]], Returns["x9", Int32[Shape('1:(a-b)*(a-c)'), ORDER_F]]]: ...
