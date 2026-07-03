@native_type(attributes=('bind(c)',))
class point:
    def __init__(
        self,
        *,
        x: Float64 = ...,
        axis: Int32 = ...
    ) -> None: ...

    x: Float64
    axis: Int32

@native_type(attributes=('bind(c)',))
class tagged_point:
    def __init__(
        self,
        *,
        weight: Complex128 = ...
    ) -> None: ...

    position: point
    weight: Complex128

def populate(
    value: tagged_point,
    x: Float64,
    axis: Int32,
    weight: Complex128
) -> None: ...

def score_by_value(
    value: tagged_point
) -> Float64: ...
