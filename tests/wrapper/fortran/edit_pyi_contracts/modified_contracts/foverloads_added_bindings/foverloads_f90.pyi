# Intentional difference: add a renamed public binding and a new Python
# overload group over two existing native specific procedures.
@bind("convert")
@native_call([Addr(Arg(0))])
def convert_int(
    value: Const(Int32)
) -> Int32: ...

@private
@bind("convert")
@native_call([Addr(Arg(0))])
def convert_real_specific(
    value: Const(Float64)
) -> Float64: ...

@overload("convert_int", generic="convert")
@native_call([Addr(Arg(0))])
def convert_number(
    value: Const(Int32)
) -> Int32: ...

@overload("convert_real_specific", generic="convert")
@native_call([Addr(Arg(0))])
def convert_number(
    value: Const(Float64)
) -> Float64: ...
