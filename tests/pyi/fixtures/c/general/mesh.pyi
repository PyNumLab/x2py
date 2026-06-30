class node(CStruct):
    id: Int
    xyz: Float64[3]

class mesh(CStruct):
    nnodes: SizeT
    nodes: Ref(node)

def node_move(
    node: Ref(node),
    delta: Const(Float64[3])
) -> None: ...

def mesh_init(
    mesh: Ref(mesh),
    nnodes: SizeT
) -> Int: ...

def mesh_clear(
    mesh: Ref(mesh)
) -> None: ...

def mesh_node_at(
    mesh: Ref(mesh),
    index: SizeT
) -> Ref(node): ...
