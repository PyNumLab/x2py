a: Int32

b: Int32

c: Int32

p_add: Int32

p_sub: Int32

p_mul: Int32

p_div: Int32

p_pow: Int32

p_mix: Int32

@call_map(NativeArg('x1', 0, source='arg', position=0, result=0, intent='inout'), NativeArg('x2', 1, source='arg', position=1, result=1, intent='inout'), NativeArg('x3', 2, source='arg', position=2, result=2, intent='inout'), NativeArg('x4', 3, source='arg', position=3, result=3, intent='inout'), NativeArg('x5', 4, source='arg', position=4, result=4, intent='inout'), NativeArg('x6', 5, source='arg', position=5, result=5, intent='inout'), NativeArg('x7', 6, source='arg', position=6, result=6, intent='inout'), NativeArg('x8', 7, source='arg', position=7, result=7, intent='inout'), NativeArg('x9', 8, source='arg', position=8, result=8, intent='inout'))
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
