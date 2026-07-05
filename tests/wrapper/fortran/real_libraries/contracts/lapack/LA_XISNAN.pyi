from x2py.contracts import Addr, Arg, Bool, Float32, Float64, bind, native_call, overload

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
def la_isnan(
    x: Float32
) -> Bool: ...

@overload("DISNAN")
def la_isnan(
    x: Float64
) -> Bool: ...
