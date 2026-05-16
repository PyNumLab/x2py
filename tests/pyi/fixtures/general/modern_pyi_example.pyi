class particle:
    id: Int32
    mass: Float64
    position: Float64[Shape('3'), FortranContiguous]

class vector3:
    values: Float64[Shape('3'), FortranContiguous]

@private
class hidden_state:
    code: Int32

counter: Int32

hidden_scale: private[Float64]

def init_particle(
    pid: Int32,
    mass: Float64,
    x: Float64,
    y: Float64,
    z: Float64
) -> particle: ...

def kinetic_energy(
    p: particle,
    vx: Float64,
    vy: Float64,
    vz: Float64
) -> Float64: ...

def scale_vector(
    v: Float64[Shape(':'), FortranContiguous],
    alpha: Float64
) -> Returns["v", Float64[Shape(':'), FortranContiguous]]: ...

def dot3(
    a: Float64[Shape('3'), FortranContiguous],
    b: Float64[Shape('3'), FortranContiguous]
) -> Float64: ...

def fill_identity3() -> Float64[Shape('3', '3'), FortranContiguous]: ...

def normalize_particle(
    p: particle
) -> Returns["p", particle]: ...

@private
def hidden_proc(
    x: Int32
) -> None: ...
