class node(CStruct):
    id: Int
    xyz: Float64[3]

class mesh(CStruct):
    nnodes: SizeT
    nodes: Addr(node)

def node_move(
    node: Addr(node),
    delta: Const(Float64[3])
) -> None: ...

def mesh_init(
    mesh: Addr(mesh),
    nnodes: SizeT
) -> Int: ...

def mesh_clear(
    mesh: Addr(mesh)
) -> None: ...

def mesh_node_at(
    mesh: Addr(mesh),
    index: SizeT
) -> Addr(node): ...
