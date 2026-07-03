@bind("SISNAN")
def sisnan(
    x: Addr(Float32)
) -> Bool: ...

@bind("DISNAN")
def disnan(
    x: Addr(Float64)
) -> Bool: ...

@overload("SISNAN")
def la_isnan(
    x: Addr(Float32)
) -> Bool: ...

@overload("DISNAN")
def la_isnan(
    x: Addr(Float64)
) -> Bool: ...
