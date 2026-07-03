class point:
    def __init__(
        self,
        *,
        x: Float64 = ...,
        y: Float64 = ...
    ) -> None: ...

    x: Float64
    y: Float64

class holder:
    def __init__(
        self,
        *,
        scale: Float64 = ...
    ) -> None: ...

    origin: point
    scale: Float64

def point_sum(
    p: Const(point)
) -> Float64: ...

@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2))])
def move_point(
    p: point,
    dx: Const(Float64),
    dy: Const(Float64)
) -> None: ...

@native_call([Return('p', 0), Addr(Arg(0)), Addr(Arg(1))])
def make_point_out(
    x: Const(Float64),
    y: Const(Float64)
) -> point: ...

@native_call([Addr(Arg(0)), Addr(Arg(1))])
def make_point(
    x: Const(Float64),
    y: Const(Float64)
) -> point: ...

def set_holder_origin(
    h: holder,
    p: Const(point)
) -> None: ...

def holder_origin_x(
    h: Const(holder)
) -> Float64: ...
