class box:
    def __init__(
        self,
        *,
        value: Int32 = ...
    ) -> None: ...

    value: Int32

def make_box(
    value: Ptr(Const(Int32))
) -> box: ...
