# Intentional difference: writable scalar, string, array, and derived-type
# arguments use immutable Python-visible inputs and explicit replacement results.
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
    base: Ptr(Const(Int32)),
    status: Annotated[Ptr(Int32), Intent("out"), Immutable]
) -> Returns["status", Int32]: ...

def fixed_inout(
    label: Annotated[Ptr(String[8]), Immutable]
) -> Returns["label", String[8]]: ...

def scale_with_status(
    values: Annotated[Float64[:], Immutable],
    status: Annotated[Ptr(Int32), Intent("out")]
) -> Returns["values", Float64[:]]: ...

def make_point(
    scale: Ptr(Const(Int32)),
    point: Annotated[summary_point, Intent("out"), Immutable]
) -> Returns["point", summary_point]: ...
