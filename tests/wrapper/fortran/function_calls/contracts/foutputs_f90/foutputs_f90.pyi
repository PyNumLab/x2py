class output_point:
    def __init__(
        self,
        *,
        x: Float64 = ...,
        tag: Int32 = ...
    ) -> None: ...

    x: Float64
    tag: Int32

@native_call([Addr(Arg(0)), Return('status', 0)])
def scalar_status(
    n: Const(Int32)
) -> Int32: ...

@native_call([Addr(Arg(0)), Arg(1)])
def fill_vector(
    n: Const(Int32),
    values: Float64[n]
) -> Returns["values", Float64[n]]: ...

@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2)])
def fill_matrix(
    n: Const(Int32),
    m: Const(Int32),
    values: Annotated[Float64[n, m], ORDER_F]
) -> Returns["values", Annotated[Float64[n, m], ORDER_F]]: ...

@native_call([Addr(Arg(0)), Return('values', 0)])
def build_alloc(
    n: Const(Int32)
) -> Annotated[Float64[:], Allocatable] | None: ...

@native_call([Addr(Arg(0)), Return('status', 1)])
def with_scalar(
    n: Const(Int32)
) -> tuple[Int32, Int32]: ...

@native_call([Addr(Arg(0)), Arg(1), Return('status', 2), Return('built', 3)])
def mixed_outputs(
    n: Const(Int32),
    values: Float64[n]
) -> tuple[Float64, Returns["values", Float64[n]], Int32, Annotated[Float64[:], Allocatable] | None]: ...

def increment(
    values: Float64[::]
) -> None: ...

@native_call([Arg(0), Return('status', 0)])
def increment_with_status(
    values: Float64[::]
) -> Int32: ...

@native_call([Return('label', 0)])
def make_label() -> String[8]: ...

@native_call([Addr(Arg(0)), Return('point', 0)])
def make_point(
    scale: Const(Int32)
) -> output_point: ...
