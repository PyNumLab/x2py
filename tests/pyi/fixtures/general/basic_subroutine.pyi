@call_map(NativeArg('x', 1, source='arg', position=1, result=0, intent='inout'))
def add1(
    n: Int32,
    x: Float64[Shape('n'), ORDER_F]
) -> Returns["x", Float64[Shape('n'), ORDER_F]]: ...
