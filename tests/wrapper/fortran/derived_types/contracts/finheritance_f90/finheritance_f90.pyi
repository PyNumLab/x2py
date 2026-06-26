class base_shape:
    def __init__(
        self,
        *,
        size: Float64 = ...
    ) -> None: ...

    size: Float64

    @bind("base_area")
    def area(self) -> Float64: ...

    @bind("base_set_size")
    def set_size(
        self,
        value: Ptr(Const(Float64))
    ) -> None: ...

class circle(base_shape):
    def __init__(
        self,
        *,
        radius: Float64 = ...
    ) -> None: ...

    radius: Float64

    @bind("circle_area")
    def area(self) -> Float64: ...

class box(base_shape):
    def __init__(
        self,
        *,
        width: Float64 = ...
    ) -> None: ...

    width: Float64

    @bind("box_area")
    def area(self) -> Float64: ...

def base_area(
    self: Annotated[Ptr(Const(base_shape)), Polymorphic]
) -> Float64: ...

def base_set_size(
    self: Annotated[Ptr(base_shape), Polymorphic],
    value: Ptr(Const(Float64))
) -> None: ...

def circle_area(
    self: Annotated[Ptr(Const(circle)), Polymorphic]
) -> Float64: ...

def box_area(
    self: Annotated[Ptr(Const(box)), Polymorphic]
) -> Float64: ...

def describe_shape(
    item: Annotated[Ptr(Const(base_shape)), Polymorphic]
) -> Float64: ...
