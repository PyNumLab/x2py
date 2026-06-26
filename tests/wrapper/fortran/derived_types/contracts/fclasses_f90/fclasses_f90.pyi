class vector:
    def __init__(
        self,
        *,
        x: Float64 = ...,
        y: Float64 = ...
    ) -> None: ...

    x: Float64
    y: Float64

    def scale(
        self,
        factor: Ptr(Const(Float64))
    ) -> None: ...

    @bind("shift_vector")
    @native_call([Arg(0), Pass(), Arg(1)])
    def shift(
        self,
        dx: Ptr(Const(Float64)),
        dy: Ptr(Const(Float64))
    ) -> None: ...

    def magnitude(self) -> Float64: ...

class vector_store:
    values: Annotated[Float64[:], Allocatable]
    matrix: Annotated[Float64[:, :], ORDER_F, Allocatable]

    def allocate_values(
        self,
        n: Ptr(Const(Int64))
    ) -> None: ...

    def set_values(
        self,
        source: Const(Float64[::Strided])
    ) -> None: ...

    def allocate_matrix(
        self,
        rows: Ptr(Const(Int64)),
        cols: Ptr(Const(Int64))
    ) -> None: ...

    def set_matrix(
        self,
        source: Annotated[Const(Float64[::Strided, ::Strided]), ORDER_F]
    ) -> None: ...

    @staticmethod
    @bind("make_vector_store")
    def make(
        n: Ptr(Const(Int64)),
        fill_value: Ptr(Const(Float64))
    ) -> vector_store: ...

def scale(
    self: Annotated[Ptr(vector), Polymorphic],
    factor: Ptr(Const(Float64))
) -> None: ...

def shift_vector(
    dx: Ptr(Const(Float64)),
    owner: Annotated[Ptr(vector), Polymorphic],
    dy: Ptr(Const(Float64))
) -> None: ...

def magnitude(
    self: Annotated[Ptr(Const(vector)), Polymorphic]
) -> Float64: ...

def allocate_values(
    self: Annotated[Ptr(vector_store), Polymorphic],
    n: Ptr(Const(Int64))
) -> None: ...

def set_values(
    self: Annotated[Ptr(vector_store), Polymorphic],
    source: Const(Float64[::Strided])
) -> None: ...

def allocate_matrix(
    self: Annotated[Ptr(vector_store), Polymorphic],
    rows: Ptr(Const(Int64)),
    cols: Ptr(Const(Int64))
) -> None: ...

def set_matrix(
    self: Annotated[Ptr(vector_store), Polymorphic],
    source: Annotated[Const(Float64[::Strided, ::Strided]), ORDER_F]
) -> None: ...

def make_vector_store(
    n: Ptr(Const(Int64)),
    fill_value: Ptr(Const(Float64))
) -> vector_store: ...
