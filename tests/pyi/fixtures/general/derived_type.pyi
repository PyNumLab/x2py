class particle:
    id: Int32
    x: Float64[Shape('3'), ORDER_F]

@call_map(NativeArg('p', 0, source='arg', position=0, result=0, intent='inout'))
def touch(
    p: particle
) -> Returns["p", particle]: ...
