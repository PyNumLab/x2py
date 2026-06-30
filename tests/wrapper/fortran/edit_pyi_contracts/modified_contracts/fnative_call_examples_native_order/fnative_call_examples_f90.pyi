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
    base: Ref(Const(Int32)),
    status: Annotated[Ref(Int32), Intent("out")]
) -> None: ...

def fill_vector(
    n: Ref(Const(Int32)),
    values: Annotated[Float64[n], Intent("out")]
) -> None: ...

def shift_matrix(
    n: Ref(Const(Int32)),
    m: Ref(Const(Int32)),
    values: Annotated[Const(Float64[n, m]), ORDER_F],
    out: Annotated[Float64[n, m], ORDER_F, Intent("out")]
) -> None: ...

def scale_with_status(
    values: Float64[::Strided],
    status: Annotated[Ref(Int32), Intent("out")]
) -> None: ...

def fixed_inout(
    label: Ref(String[8])
) -> None: ...

def make_label(
    label: Annotated[Ref(String[6]), Intent("out")]
) -> None: ...

def summarize_mixed(
    n: Ref(Const(Int32)),
    values: Annotated[Float64[n], Intent("out")],
    status: Annotated[Ref(Int32), Intent("out")],
    label: Annotated[Ref(String[6]), Intent("out")]
) -> Float64: ...

def make_point(
    scale: Ref(Const(Int32)),
    point: Annotated[summary_point, Intent("out")]
) -> None: ...
