class point_t:
    def __init__(
        self,
        *,
        x: Float64 = ...,
        y: Float64 = ...
    ) -> None: ...

    x: Float64
    y: Float64

@native_call([Arg(0), Addr(Arg(1))])
def apply_value_callback(
    callback: Callable[[Int32], Int32],
    value: Int32
) -> Int32: ...

@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Return('output', 0)])
def apply_scalar_storage_callback(
    callback: Callable[[InOut(Float64), Out(Float64), PassByRef(Float64)], None],
    value: Float64,
    missing: Float64
) -> Float64: ...

@native_call([Arg(0), Addr(Arg(1)), Arg(2), Arg(3)])
def apply_array_storage_callback(
    callback: Callable[[In(Int32), In(Float64[count]), Out(Float64[count])], None],
    count: Int32,
    values: Float64[count],
    output: Float64[count]
) -> Returns["output", Float64[count]]: ...

@native_call([Arg(0), Arg(1), Return('write_label', 1)])
def apply_string_storage_callback(
    callback: Callable[[In(String[8]), Out(String[8][()]), InOut(String[8][()])], None],
    update_label: String[8]
) -> tuple[Returns["update_label", String[8]], String[8]]: ...

@native_call([Arg(0), Arg(1), Return('output', 0)])
def apply_point_callback(
    callback: Callable[[In(point_t)], point_t],
    value: point_t
) -> point_t: ...
