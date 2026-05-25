class particle:
    id: Int32
    x: Float64[3]

current_particle: private[particle]

def particle_touch(
    p: Ptr(particle)
) -> None: ...

def particle_reset(
    p: Ptr(particle)
) -> None: ...

def particle_move(
    p: Ptr(particle),
    delta: Const(Float64[3])
) -> None: ...

def particle_current() -> Ptr(Const(particle)): ...
