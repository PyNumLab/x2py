class summary_point:
    def __init__(
        self,
        *,
        total: Float64 = ...,
        code: Int32 = ...
    ) -> None: ...

    total: Float64
    code: Int32

@native_call([Ref(Arg(0)), Return('status', 0)])
def scalar_status(
    base: Const(Int32)
) -> Int32: ...

@native_call([Ref(Arg(0)), Arg(1)])
def fill_vector(
    n: Const(Int32),
    values: Float64[n]
) -> Returns["values", Float64[n]]: ...

@native_call([Ref(Arg(0)), Ref(Arg(1)), Arg(2), Arg(3)])
def shift_matrix(
    n: Const(Int32),
    m: Const(Int32),
    values: Annotated[Const(Float64[n, m]), ORDER_F],
    out: Annotated[Float64[n, m], ORDER_F]
) -> Returns["out", Annotated[Float64[n, m], ORDER_F]]: ...

@native_call([Arg(0), Return('status', 0)])
def scale_with_status(
    values: Float64[::Strided]
) -> Int32: ...

@native_call([Arg(0)])
def fixed_inout(
    label: Ref(String[8])
) -> Returns["label", Ref(String[8])]: ...

@native_call([Return('label', 0)])
def make_label() -> String[6]: ...

@native_call([Ref(Arg(0)), Arg(1), Return('status', 2), Return('label', 3)])
def summarize_mixed(
    n: Const(Int32),
    values: Float64[n]
) -> tuple[Float64, Returns["values", Float64[n]], Int32, String[6]]: ...

@native_call([Ref(Arg(0)), Return('point', 0)])
def make_point(
    scale: Const(Int32)
) -> summary_point: ...
