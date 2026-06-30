# Intentional difference: add a renamed public binding and a new Python
# overload group over two existing native specific procedures.
@bind("convert")
def convert_int(
    value: Ref(Const(Int32))
) -> Int32: ...

@private
@bind("convert")
def convert_real_specific(
    value: Ref(Const(Float64))
) -> Float64: ...

@overload("convert_int", generic="convert")
def convert_number(
    value: Ref(Const(Int32))
) -> Int32: ...

@overload("convert_real_specific", generic="convert")
def convert_number(
    value: Ref(Const(Float64))
) -> Float64: ...
