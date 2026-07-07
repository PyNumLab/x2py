from x2py.contracts import Addr, Allocatable, Arg, Float64, Int32, native_call

class child:
    def __init__(
        self,
        *,
        id: Int32 = 0
    ) -> None: ...

    id: Int32 = 0

class box:
    def __init__(
        self,
        *,
        scalar: Int32 = 0
    ) -> None: ...

    scalar: Int32 = 0
    fixed: Float64[2] = [0.0, 0.0]
    values: Allocatable[Float64[:]]
    nested: child

    def scalar_plus_nested(self) -> Int32: ...

current: box

@native_call([Addr(Arg(0))])
def initialise_current(
    n: Int32
) -> None: ...

def mutate_current() -> None: ...

def release_current() -> None: ...

def current_total() -> Float64: ...
