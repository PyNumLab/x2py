class particle:
    id: Int32
    mass: Float64
    position: Float64[Shape('3'), ORDER_F]

class vector3:
    values: Float64[Shape('3'), ORDER_F]

@private
class hidden_state:
    code: Int32

counter: Int32

hidden_scale: private[Float64]

@call_map(NativeArg('p', 0, source='return', position=0, intent='out'), NativeArg('pid', 1, source='arg', position=0), NativeArg('mass', 2, source='arg', position=1), NativeArg('x', 3, source='arg', position=2), NativeArg('y', 4, source='arg', position=3), NativeArg('z', 5, source='arg', position=4))
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

@call_map(NativeArg('v', 0, source='arg', position=0, result=0, intent='inout'))
def scale_vector(
    v: Float64[Shape(':'), ORDER_F],
    alpha: Float64
) -> Returns["v", Float64[Shape(':'), ORDER_F]]: ...

def dot3(
    a: Float64[Shape('3'), ORDER_F],
    b: Float64[Shape('3'), ORDER_F]
) -> Float64: ...

@call_map(NativeArg('a', 0, source='return', position=0, intent='out'))
def fill_identity3() -> Float64[Shape('3', '3'), ORDER_F]: ...

@call_map(NativeArg('p', 0, source='arg', position=0, result=0, intent='inout'))
def normalize_particle(
    p: particle
) -> Returns["p", particle]: ...

@private
def hidden_proc(
    x: Int32
) -> None: ...
