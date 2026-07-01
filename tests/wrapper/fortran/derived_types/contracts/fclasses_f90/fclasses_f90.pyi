class vector:
    def __init__(
        self,
        *,
        x: Float64 = ...,
        y: Float64 = ...
    ) -> None: ...

    x: Float64
    y: Float64

    @native_call([Pass(), Ref(Arg(0))])
    def scale(
        self,
        factor: Const(Float64)
    ) -> None: ...

    @bind("shift_vector")
    @native_call([Ref(Arg(0)), Pass(), Ref(Arg(1))])
    def shift(
        self,
        dx: Const(Float64),
        dy: Const(Float64)
    ) -> None: ...

    def magnitude(self) -> Float64: ...

class vector_store:
    def __init__(self) -> None: ...

    values: Annotated[Float64[:], Allocatable]
    matrix: Annotated[Float64[:, :], ORDER_F, Allocatable]

    @native_call([Pass(), Ref(Arg(0))])
    def allocate_values(
        self,
        n: Const(Int64)
    ) -> None: ...

    def set_values(
        self,
        source: Const(Float64[::])
    ) -> None: ...

    @native_call([Pass(), Ref(Arg(0)), Ref(Arg(1))])
    def allocate_matrix(
        self,
        rows: Const(Int64),
        cols: Const(Int64)
    ) -> None: ...

    def set_matrix(
        self,
        source: Annotated[Const(Float64[::, ::]), ORDER_F]
    ) -> None: ...

    @staticmethod
    @bind("make_vector_store")
    @native_call([Ref(Arg(0)), Ref(Arg(1))])
    def make(
        n: Const(Int64),
        fill_value: Const(Float64)
    ) -> vector_store: ...

@native_call([Arg(0), Ref(Arg(1))])
def scale(
    self: Annotated[Ref(vector), Polymorphic],
    factor: Const(Float64)
) -> None: ...

@native_call([Ref(Arg(0)), Arg(1), Ref(Arg(2))])
def shift_vector(
    dx: Const(Float64),
    owner: Annotated[Ref(vector), Polymorphic],
    dy: Const(Float64)
) -> None: ...

def magnitude(
    self: Annotated[Ref(Const(vector)), Polymorphic]
) -> Float64: ...

@native_call([Arg(0), Ref(Arg(1))])
def allocate_values(
    self: Annotated[Ref(vector_store), Polymorphic],
    n: Const(Int64)
) -> None: ...

def set_values(
    self: Annotated[Ref(vector_store), Polymorphic],
    source: Const(Float64[::])
) -> None: ...

@native_call([Arg(0), Ref(Arg(1)), Ref(Arg(2))])
def allocate_matrix(
    self: Annotated[Ref(vector_store), Polymorphic],
    rows: Const(Int64),
    cols: Const(Int64)
) -> None: ...

def set_matrix(
    self: Annotated[Ref(vector_store), Polymorphic],
    source: Annotated[Const(Float64[::, ::]), ORDER_F]
) -> None: ...

@native_call([Ref(Arg(0)), Ref(Arg(1))])
def make_vector_store(
    n: Const(Int64),
    fill_value: Const(Float64)
) -> vector_store: ...
