class node:
    id: Int32
    xyz: Float64[Shape('3'), ORDER_F]

class mesh:
    nnodes: Int32
    nodes: node[Shape(':'), ORDER_F, Allocatable]
