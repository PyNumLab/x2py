class particle:
    id: Int32
    x: Float64[Shape('3'), FortranContiguous]

def touch(
    p: particle
) -> Returns["p", particle]: ...
