# Intentional difference: no native-call decorators.  Output slots stay
# visible in native dummy-argument order.
class summary_point:
    def __init__(
        self,
        *,
        total: Float64 = ...,
        code: Int32 = ...
    ) -> None: ...

    total: Float64
    code: Int32

def scalar_status(
    base: Const(Int32[()]),
    status: Annotated[Int32[()], Intent("out")]
) -> None: ...

@bind("scalar_status")
def scalar_status_raw(
    base: Addr(Const(Int32)),
    status: Annotated[Addr(Int32), Intent("out")]
) -> None: ...

def fill_vector(
    n: Const(Int32[()]),
    values: Annotated[Float64[n], Intent("out")]
) -> None: ...

@bind("fill_vector")
def fill_vector_raw(
    n: Const(Int32[()]),
    values: Annotated[Addr(Float64[n]), Intent("out")]
) -> None: ...

def shift_matrix(
    n: Const(Int32[()]),
    m: Const(Int32[()]),
    values: Annotated[Const(Float64[n, m]), ORDER_F],
    out: Annotated[Float64[n, m], ORDER_F, Intent("out")]
) -> None: ...

def scale_with_status(
    values: Float64[::],
    status: Annotated[Int32[()], Intent("out")]
) -> None: ...

def fixed_inout(
    label: String[8]
) -> None: ...

@bind("fixed_inout")
def fixed_inout_raw(
    label: Addr(String[8])
) -> None: ...

def make_label(
    label: Annotated[String[6], Intent("out")]
) -> None: ...

def summarize_mixed(
    n: Const(Int32[()]),
    values: Annotated[Float64[n], Intent("out")],
    status: Annotated[Int32[()], Intent("out")],
    label: Annotated[String[6], Intent("out")]
) -> Float64: ...

def make_point(
    scale: Const(Int32[()]),
    point: Annotated[summary_point, Intent("out")]
) -> None: ...
