a: Int32

b: Int32

c: Int32

p_add: Int32

p_sub: Int32

p_mul: Int32

p_div: Int32

p_pow: Int32

p_mix: Int32

def all_exprs(
    x1: Int32[Shape('1:p_add'), FortranContiguous],
    x2: Int32[Shape('1:p_sub'), FortranContiguous],
    x3: Int32[Shape('1:p_mul'), FortranContiguous],
    x4: Int32[Shape('1:p_div'), FortranContiguous],
    x5: Int32[Shape('1:p_pow'), FortranContiguous],
    x6: Int32[Shape('0:p_mix'), FortranContiguous],
    x7: Int32[Shape('1:-(-a + b)'), FortranContiguous],
    x8: Int32[Shape('1:(a+b)*(c+1)-1'), FortranContiguous],
    x9: Int32[Shape('1:(a-b)*(a-c)'), FortranContiguous]
) -> None: ...
