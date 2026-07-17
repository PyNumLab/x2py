from x2py.contracts import Addr, Arg, Float64, Int32, Return, Returns, String, native_call

class summary_point:
    def __init__(
        self,
        *,
        total: Float64 = ...,
        code: Int32 = ...
    ) -> None: ...

    total: Float64
    code: Int32

@native_call([Addr(Arg(0)), Return('status', 0)])
def scalar_status(
    base: Int32
) -> Int32: ...

@native_call([Addr(Arg(0)), Arg(1)])
def fill_vector(
    n: Int32,
    values: Float64[n]
) -> Returns["values", Float64[n]]: ...

@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Arg(3)])
def shift_matrix(
    n: Int32,
    m: Int32,
    values: Float64[n, m],
    out: Float64[n, m]
) -> Returns["out", Float64[n, m]]: ...

@native_call([Arg(0), Return('status', 0)])
def scale_with_status(
    values: Float64[::]
) -> Int32: ...

def fixed_inout(
    label: String[8]
) -> Returns["label", String[8]]: ...

@native_call([Return('label', 0)])
def make_label() -> String[6]: ...

@native_call([Addr(Arg(0)), Arg(1), Return('status', 2), Return('label', 3)])
def summarize_mixed(
    n: Int32,
    values: Float64[n]
) -> tuple[Float64, Returns["values", Float64[n]], Int32, String[6]]: ...

@native_call([Addr(Arg(0)), Return('point', 0)])
def make_point(
    scale: Int32
) -> summary_point: ...
