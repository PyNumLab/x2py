@external
def fill_grid(
    x: Annotated[Int32[::, ::], ORDER_F]
) -> None: ...

@external
def update_plane(
    x: Annotated[Float32[::, ::], ORDER_F]
) -> None: ...

@external
def step(
    state: Addr(sim_state)
) -> None: ...
