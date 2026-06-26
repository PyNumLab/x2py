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
    p: Ptr(Const(point))
) -> Float64: ...

def move_point(
    p: Ptr(point),
    dx: Ptr(Const(Float64)),
    dy: Ptr(Const(Float64))
) -> None: ...

@native_call([Return('p', 0), Arg(0), Arg(1)])
def make_point_out(
    x: Ptr(Const(Float64)),
    y: Ptr(Const(Float64))
) -> point: ...

def make_point(
    x: Ptr(Const(Float64)),
    y: Ptr(Const(Float64))
) -> point: ...

def set_holder_origin(
    h: Ptr(holder),
    p: Ptr(Const(point))
) -> None: ...

def holder_origin_x(
    h: Ptr(Const(holder))
) -> Float64: ...
