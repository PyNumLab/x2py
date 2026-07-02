class box:
    def __init__(self) -> None: ...

    values: Annotated[Float64[:], Allocatable]

    @native_call([Pass(), Ref(Arg(0))])
    def allocate_values(
        self,
        n: Const(Int32)
    ) -> None: ...

    def values_sum(self) -> Float64: ...

current: Annotated[box, Aliased]

@native_call([Ref(Arg(0))])
def allocate_current(
    n: Const(Int32)
) -> None: ...

def deallocate_current() -> None: ...

def current_sum() -> Float64: ...
