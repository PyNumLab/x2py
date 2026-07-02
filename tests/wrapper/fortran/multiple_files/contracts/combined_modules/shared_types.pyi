class box:
    def __init__(
        self,
        *,
        value: Int32 = ...
    ) -> None: ...

    value: Int32

@native_call([Ref(Arg(0))])
def make_box(
    value: Const(Int32)
) -> box: ...
