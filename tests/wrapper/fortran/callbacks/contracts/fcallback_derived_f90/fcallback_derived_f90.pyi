from x2py.contracts import Arg, Float64, Return, native_call, prototype

class point_t:
    def __init__(
        self,
        *,
        x: Float64 = ...,
        y: Float64 = ...
    ) -> None: ...

    x: Float64
    y: Float64

@prototype
def point_callback(
    value: point_t
) -> point_t: ...

@native_call([Arg(0), Arg(1), Return('output', 0)])
def apply_point(
    callback: point_callback,
    value: point_t
) -> point_t: ...
