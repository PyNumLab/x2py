class node:
    id: Int32
    xyz: Float64[Shape('3'), FortranContiguous]

class mesh:
    nnodes: Int32
    nodes: node[Shape(':'), FortranContiguous, Allocatable]
