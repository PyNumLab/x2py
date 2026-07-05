from x2py.contracts import Annotated, Float32, Int32, ORDER_F, external

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
    state: sim_state
) -> None: ...
