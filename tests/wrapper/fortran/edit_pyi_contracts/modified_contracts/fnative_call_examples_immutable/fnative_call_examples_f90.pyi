# Intentional difference: values is immutable and returns a replacement copy.
from x2py.contracts import Annotated, Float64, Immutable, Int32, Returns

def scale_with_status(
    values: Annotated[Float64[:], Immutable],
    status: Int32[()]
) -> Returns["values", Float64[:]]: ...
