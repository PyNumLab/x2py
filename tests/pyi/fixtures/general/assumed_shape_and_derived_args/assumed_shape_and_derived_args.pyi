from x2py.contracts import Float32, Int32, external

@external
def fill_grid(
    x: Int32[::, ::]
) -> None: ...

@external
def update_plane(
    x: Float32[::, ::]
) -> None: ...

@external
def step(
    state: sim_state
) -> None: ...
