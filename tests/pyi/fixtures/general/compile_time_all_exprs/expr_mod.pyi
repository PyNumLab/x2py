a: Final[Int32] = 8

b: Final[Int32] = 3

c: Final[Int32] = 2

p_add: Final[Int32] = a + b

p_sub: Final[Int32] = a - b

p_mul: Final[Int32] = b * c

p_div: Final[Int32] = a / c

p_pow: Final[Int32] = c ** b

p_mix: Final[Int32] = (a + b) * c - 1

def all_exprs(
    x1: Int32[p_add],
    x2: Int32[p_sub],
    x3: Int32[p_mul],
    x4: Int32[p_div],
    x5: Int32[p_pow],
    x6: Int32[p_mix - 0 + 1],
    x7: Int32[-(-a + b)],
    x8: Int32[(a + b) * (c + 1) - 1],
    x9: Int32[(a - b) * (a - c)]
) -> None: ...
