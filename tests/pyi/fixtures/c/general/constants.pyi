COORD_X: Final[Int32]

COORD_Y: Final[Int32]

COORD_Z: Final[Int32]

X2PY_GENERAL_NMAX: Final[Int32]

X2PY_GENERAL_ORIGIN_RANK: Final[Int32]

nmax: Int32

origin: Float64[3]

def coordinate_axis_name(
    axis: Int32
) -> Ptr(Const(Int8)): ...

def coordinate_axis_count() -> SizeT: ...
