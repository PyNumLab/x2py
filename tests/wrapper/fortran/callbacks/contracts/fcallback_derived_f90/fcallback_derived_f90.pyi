class point_t:
    def __init__(
        self,
        *,
        x: Float64 = ...,
        y: Float64 = ...
    ) -> None: ...

    x: Float64
    y: Float64

@native_call([Arg(0), Arg(1), Return('output', 0)])
def apply_point(
    callback: Callable[[Ptr(Const(point_t))], point_t],
    value: Ptr(Const(point_t))
) -> point_t: ...
