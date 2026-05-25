class modern_particle:
    id: Int32
    mass: Float64
    position: Float64[3]

class vector3:
    values: Float64[3]

modern_counter: Int32

hidden_scale: private[Float64]

def init_particle(
    p: Ptr(modern_particle),
    pid: Int32,
    mass: Float64,
    x: Float64,
    y: Float64,
    z: Float64
) -> None: ...

def kinetic_energy(
    p: Ptr(modern_particle),
    vx: Float64,
    vy: Float64,
    vz: Float64
) -> Float64: ...

def scale_vector(
    n: Int32,
    v: Float64[1],
    alpha: Float64
) -> None: ...

def dot3(
    a: Const(Float64[3]),
    b: Const(Float64[3])
) -> Float64: ...

def fill_identity3_modern(
    a: Float64[3, 3]
) -> None: ...

def normalize_particle(
    p: Ptr(modern_particle)
) -> None: ...
