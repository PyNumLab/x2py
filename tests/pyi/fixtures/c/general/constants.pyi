class coordinate_axis(Enum[Int]):
    pass

COORD_X: Final[coordinate_axis] = 0

COORD_Y: Final[coordinate_axis] = 1

COORD_Z: Final[coordinate_axis] = 2

X2PY_GENERAL_NMAX: Final[Int32]

X2PY_GENERAL_ORIGIN_RANK: Final[Int32]

nmax: Int

origin: Float64[3]

def coordinate_axis_name(
    axis: coordinate_axis
) -> Ptr(Const(Int8)): ...

def coordinate_axis_count() -> SizeT: ...
