from x2py.contracts import Addr, Arg, Int32, bind, external, native_call

@external
@bind("fixed_add")
@native_call([Addr(Arg(0))])
def renamed_increment(value: Int32) -> Int32: ...
