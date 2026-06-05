class node(CStruct):
    id: Int
    xyz: Float64[3]

class mesh(CStruct):
    nnodes: SizeT
    nodes: Ptr(node)

def node_move(
    node: Ptr(node),
    delta: Const(Float64[3])
) -> None: ...

def mesh_init(
    mesh: Ptr(mesh),
    nnodes: SizeT
) -> Int: ...

def mesh_clear(
    mesh: Ptr(mesh)
) -> None: ...

def mesh_node_at(
    mesh: Ptr(mesh),
    index: SizeT
) -> Ptr(node): ...
