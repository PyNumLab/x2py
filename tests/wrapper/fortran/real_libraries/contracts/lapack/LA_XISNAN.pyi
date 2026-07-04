@bind("SISNAN")
@native_call([Addr(Arg(0))])
def sisnan(
    x: Float32
) -> Bool: ...

@bind("DISNAN")
@native_call([Addr(Arg(0))])
def disnan(
    x: Float64
) -> Bool: ...

@overload("SISNAN")
@native_call([Addr(Arg(0))])
def la_isnan(
    x: Float32
) -> Bool: ...

@overload("DISNAN")
@native_call([Addr(Arg(0))])
def la_isnan(
    x: Float64
) -> Bool: ...
