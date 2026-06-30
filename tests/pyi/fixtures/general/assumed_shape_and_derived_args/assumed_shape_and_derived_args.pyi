@external
def fill_grid(
    x: Annotated[Int32[::Strided, ::Strided], ORDER_F]
) -> None: ...

@external
def update_plane(
    x: Annotated[Float32[::Strided, ::Strided], ORDER_F]
) -> None: ...

@external
def step(
    state: Ref(sim_state)
) -> None: ...
