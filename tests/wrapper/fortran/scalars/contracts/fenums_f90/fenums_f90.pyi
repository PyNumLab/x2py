class paint:
    def __init__(
        self,
        *,
        color: Int32 = red
    ) -> None: ...

    color: Int32 = red

red: Final[Int32] = -1

blue: Final[Int32] = 0

green: Final[Int32] = 10

yellow: Final[Int32] = 11

def round_trip_color(
    color: Ptr(Const(Int32))
) -> Int32: ...
