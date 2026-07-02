@bind("SISNAN")
def sisnan(
    x: Ref(Float32)
) -> Bool: ...

@bind("DISNAN")
def disnan(
    x: Ref(Float64)
) -> Bool: ...

@overload("SISNAN")
def la_isnan(
    x: Ref(Float32)
) -> Bool: ...

@overload("DISNAN")
def la_isnan(
    x: Ref(Float64)
) -> Bool: ...
