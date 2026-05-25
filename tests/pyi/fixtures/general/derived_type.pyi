class particle:
    id: Int32
    x: Float64[3]

def touch(
    p: Ptr(particle)
) -> None: ...
