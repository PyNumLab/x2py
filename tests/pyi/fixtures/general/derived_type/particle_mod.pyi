class particle:
    def __init__(
        self,
        *,
        id: Int32 = ...
    ) -> None: ...

    id: Int32
    x: Float64[3]

def touch(
    p: particle
) -> None: ...
