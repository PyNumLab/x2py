from x2py.contracts import Addr, Annotated, Arg, Float64, Pass, Polymorphic, bind, native_call


class vector:
    @bind("shift")
    def __init__(self, dx: Float64, dy: Float64) -> None: ...

    x: Float64
    y: Float64

    @bind("shift_vector")
    @native_call([Addr(Arg(0)), Pass(), Addr(Arg(1))])
    def shift(self, dx: Float64, dy: Float64) -> None: ...


@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def shift_vector(
    dx: Float64,
    owner: Annotated[vector, Polymorphic],
    dy: Float64,
) -> None: ...
