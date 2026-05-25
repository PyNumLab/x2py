X2PY_EXPR_N0: Final[Int32]

X2PY_EXPR_N1: Final[Int32]

X2PY_EXPR_A: Final[Int32]

X2PY_EXPR_B: Final[Int32]

X2PY_EXPR_C: Final[Int32]

def fill_grid(
    x: Int32[1, X2PY_EXPR_N1]
) -> None: ...

def update_plane(
    n: Int32,
    x: Float32[1, n]
) -> None: ...

def use_expr(
    x: Int32[X2PY_EXPR_N1],
    y: Float32[X2PY_EXPR_N0 * 2]
) -> None: ...

def all_exprs(
    x1: Int32[X2PY_EXPR_A + X2PY_EXPR_B],
    x2: Int32[X2PY_EXPR_A - X2PY_EXPR_B],
    x3: Int32[X2PY_EXPR_B * X2PY_EXPR_C],
    x4: Int32[X2PY_EXPR_A / X2PY_EXPR_C],
    x5: Int32[1 << X2PY_EXPR_B],
    x6: Int32[(X2PY_EXPR_A + X2PY_EXPR_B) * X2PY_EXPR_C - 1],
    x7: Int32[-(-X2PY_EXPR_A + X2PY_EXPR_B)],
    x8: Int32[(X2PY_EXPR_A + X2PY_EXPR_B) * (X2PY_EXPR_C + 1) - 1],
    x9: Int32[(X2PY_EXPR_A - X2PY_EXPR_B) * (X2PY_EXPR_A - X2PY_EXPR_C)]
) -> None: ...
