from x2py.contracts import Allocatable, Float64, Int32

class node:
    def __init__(
        self,
        *,
        id: Int32 = ...
    ) -> None: ...

    id: Int32
    xyz: Float64[3]

class mesh:
    def __init__(
        self,
        *,
        nnodes: Int32 = ...
    ) -> None: ...

    nnodes: Int32
    nodes: Allocatable[node[:]]
