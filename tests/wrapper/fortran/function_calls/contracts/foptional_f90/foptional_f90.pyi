class sample:
    def __init__(
        self,
        *,
        value: Int32 = ...
    ) -> None: ...

    value: Int32

@native_call([Ref(Arg(0)), Ref(Arg(1)), Arg(2), Arg(3), Arg(4)])
def summarize(
    required: Const(Int32),
    scale: Const(Int32) = ...,
    values: Const(Float64[::]) = ...,
    label: Ref(Const(String)) = ...,
    item: Ref(Const(sample)) = ...
) -> Int32: ...

@native_call([Arg(0), Ref(Arg(1))])
def mutate_optional(
    values: Float64[::] = ...,
    amount: Const(Float64) = ...
) -> None: ...

@native_call([Ref(Arg(0)), Arg(1)])
def fill_optional(
    n: Const(Int32),
    values: Float64[::] = ...
) -> Returns["values", Float64[::], Optional]: ...

@native_call([Ref(Arg(0)), Return('status', 1)])
def optional_status(
    base: Const(Int32)
) -> tuple[Int32, Int32 | None]: ...
