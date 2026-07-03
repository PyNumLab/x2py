class particle(CStruct):
    id: Int
    x: Float64[3]

current_particle: private[particle]

def particle_touch(
    p: Addr(particle)
) -> None: ...

def particle_reset(
    p: Addr(particle)
) -> None: ...

def particle_move(
    p: Addr(particle),
    delta: Const(Float64[3])
) -> None: ...

def particle_current() -> Addr(Const(particle)): ...
