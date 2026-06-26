class sample:
    def __init__(
        self,
        *,
        value: Int32 = ...
    ) -> None: ...

    value: Int32

def summarize(
    required: Ptr(Const(Int32)),
    scale: Ptr(Const(Int32)) = ...,
    values: Const(Float64[::Strided]) = ...,
    label: Ptr(Const(String)) = ...,
    item: Ptr(Const(sample)) = ...
) -> Int32: ...

def mutate_optional(
    values: Float64[::Strided] = ...,
    amount: Ptr(Const(Float64)) = ...
) -> None: ...

@native_call([Arg(0), Arg(1)])
def fill_optional(
    n: Ptr(Const(Int32)),
    values: Float64[::Strided] = ...
) -> Returns["values", Float64[::Strided], Optional]: ...

@native_call([Arg(0), Return('status', 1)])
def optional_status(
    base: Ptr(Const(Int32))
) -> tuple[Int32, Int32 | None]: ...
