# Intentional difference: values is immutable and returns a replacement copy.
def scale_with_status(
    values: Annotated[Float64[:], Immutable],
    status: Annotated[Ptr(Int32), Intent("out")]
) -> Returns["values", Float64[:]]: ...
