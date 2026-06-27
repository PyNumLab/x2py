@bind("SISNAN")
def sisnan(
    x: Ptr(Float32)
) -> Bool: ...

@bind("DISNAN")
def disnan(
    x: Ptr(Float64)
) -> Bool: ...

@overload("SISNAN")
def la_isnan(
    x: Ptr(Float32)
) -> Bool: ...

@overload("DISNAN")
def la_isnan(
    x: Ptr(Float64)
) -> Bool: ...
