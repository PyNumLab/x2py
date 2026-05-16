def norm2(
    x: Float64[Shape(':'), FortranContiguous]
) -> Float64: ...

def scale(
    a: Float64,
    x: Float64[Shape(':'), FortranContiguous]
) -> Returns["x", Float64[Shape(':'), FortranContiguous]]: ...
