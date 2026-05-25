class node:
    id: Int32
    xyz: Float64[3]

class mesh:
    nnodes: Int32
    nodes: Annotated[node[:], Allocatable, ArrayCategory('deferred_shape')]
