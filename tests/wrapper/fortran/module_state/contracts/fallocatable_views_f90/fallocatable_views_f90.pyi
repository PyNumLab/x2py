class buffer:
    def __init__(self) -> None: ...

    values: Annotated[Float64[:], Allocatable]

    def allocate_values(
        self,
        n: Ptr(Const(Int32))
    ) -> None: ...

    def deallocate_values(self) -> None: ...

    def scale_values(
        self,
        scale: Ptr(Const(Float64))
    ) -> None: ...

    def values_sum(self) -> Float64: ...

module_values: Annotated[Float64[:], Allocatable, FortranTarget] | None

def allocate_module_values(
    n: Ptr(Const(Int32))
) -> None: ...

def deallocate_module_values() -> None: ...

def scale_module_values(
    scale: Ptr(Const(Float64))
) -> None: ...

def module_values_sum() -> Float64: ...

@native_call([Arg(0), Return('values', 0)])
def build_values(
    n: Ptr(Const(Int32))
) -> Annotated[Float64[:], Allocatable] | None: ...

@native_call([Arg(0), Arg(1), Return('values', 0)])
def build_matrix(
    n: Ptr(Const(Int32)),
    m: Ptr(Const(Int32))
) -> Annotated[Float64[:, :], ORDER_F, Allocatable] | None: ...

def make_values(
    n: Ptr(Const(Int32))
) -> Annotated[Float64[:], Allocatable]: ...

def make_matrix(
    n: Ptr(Const(Int32)),
    m: Ptr(Const(Int32))
) -> Annotated[Float64[:, :], ORDER_F, Allocatable]: ...
