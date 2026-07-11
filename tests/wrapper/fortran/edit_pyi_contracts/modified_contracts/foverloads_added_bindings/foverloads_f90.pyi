# Intentional difference: add a renamed public binding and a new Python
# overload group over two existing native specific procedures.
from x2py.contracts import Addr, Arg, Float64, Int32, bind, native_call, overload, private

@bind("convert")
@native_call([Addr(Arg(0))])
def convert_int(
    value: Int32
) -> Int32: ...

@private
@bind("convert")
@native_call([Addr(Arg(0))])
def convert_real_specific(
    value: Float64
) -> Float64: ...

@overload("convert_int", generic="convert")
def convert_number(
    value: Int32
) -> Int32: ...

@overload("convert_real_specific", generic="convert")
def convert_number(
    value: Float64
) -> Float64: ...
