def norm2(
    x: Float64[Shape(':'), ORDER_F]
) -> Float64: ...

@call_map(NativeArg('x', 1, source='arg', position=1, result=0, intent='inout'))
def scale(
    a: Float64,
    x: Float64[Shape(':'), ORDER_F]
) -> Returns["x", Float64[Shape(':'), ORDER_F]]: ...
