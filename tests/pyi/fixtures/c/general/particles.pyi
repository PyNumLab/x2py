class particle(CStruct):
    id: Int
    x: Float64[3]

current_particle: private[particle]

def particle_touch(
    p: Ref(particle)
) -> None: ...

def particle_reset(
    p: Ref(particle)
) -> None: ...

def particle_move(
    p: Ref(particle),
    delta: Const(Float64[3])
) -> None: ...

def particle_current() -> Ref(Const(particle)): ...
