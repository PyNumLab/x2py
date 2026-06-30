class particle:
    def __init__(
        self,
        *,
        id: Int32 = ...,
        mass: Float64 = ...
    ) -> None: ...

    id: Int32
    mass: Float64
    position: Float64[3]

class vector3:
    def __init__(self) -> None: ...

    values: Float64[3]

counter: Int32

@native_call([Return('p', 0), Ref(Arg(0)), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3)), Ref(Arg(4))])
def init_particle(
    pid: Const(Int32),
    mass: Const(Float64),
    x: Const(Float64),
    y: Const(Float64),
    z: Const(Float64)
) -> particle: ...

@native_call([Arg(0), Ref(Arg(1)), Ref(Arg(2)), Ref(Arg(3))])
def kinetic_energy(
    p: Ref(Const(particle)),
    vx: Const(Float64),
    vy: Const(Float64),
    vz: Const(Float64)
) -> Float64: ...

@native_call([Arg(0), Ref(Arg(1))])
def scale_vector(
    v: Float64[::Strided],
    alpha: Const(Float64)
) -> None: ...

def dot3(
    a: Const(Float64[3]),
    b: Const(Float64[3])
) -> Float64: ...

@native_call([Arg(0)])
def fill_identity3(
    a: Annotated[Float64[3, 3], ORDER_F]
) -> Returns["a", Annotated[Float64[3, 3], ORDER_F]]: ...

def normalize_particle(
    p: Ref(particle)
) -> None: ...
