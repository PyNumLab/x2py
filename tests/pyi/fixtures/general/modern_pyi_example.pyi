class particle:
    id: Int32
    mass: Float64
    position: Float64[3]

class vector3:
    values: Float64[3]

@private
class hidden_state:
    code: Int32

counter: Int32

hidden_scale: private[Float64]

def init_particle(
    p: Annotated[Ptr(particle), Intent('out')],
    pid: Ptr(Const(Int32)),
    mass: Ptr(Const(Float64)),
    x: Ptr(Const(Float64)),
    y: Ptr(Const(Float64)),
    z: Ptr(Const(Float64))
) -> None: ...

def kinetic_energy(
    p: Ptr(Const(particle)),
    vx: Ptr(Const(Float64)),
    vy: Ptr(Const(Float64)),
    vz: Ptr(Const(Float64))
) -> Float64: ...

def scale_vector(
    v: Float64[::Strided],
    alpha: Ptr(Const(Float64))
) -> None: ...

def dot3(
    a: Const(Float64[3]),
    b: Const(Float64[3])
) -> Float64: ...

def fill_identity3(
    a: Annotated[Float64[3, 3], ORDER_F, Intent('out')]
) -> None: ...

def normalize_particle(
    p: Ptr(particle)
) -> None: ...

@private
def hidden_proc(
    x: Ptr(Const(Int32))
) -> None: ...
