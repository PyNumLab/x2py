from x2py.contracts import Addr, Aliased, Annotated, Arg, Destruction, Float64, Int32, Ownership, Pointer, PointerAssociation, Transfer, native_call

@native_call([Addr(Arg(0))])
def read_pointer(
    value: Annotated[Float64, PointerAssociation("runtime"), Ownership("caller"), Transfer("call_local"), Destruction("call_local")]
) -> Float64: ...

@native_call([Addr(Arg(0)), Addr(Arg(1))])
def pointer_to_scalar(
    value: Annotated[Float64, Aliased],
    use_value: Int32
) -> Annotated[Addr(Float64), PointerAssociation("runtime"), Ownership("python"), Transfer("snapshot_copy"), Destruction("python_refcount")]: ...

def sum_pointer(
    values: Annotated[Float64[:], Pointer, PointerAssociation("runtime"), Ownership("caller"), Transfer("call_local"), Destruction("none")]
) -> Float64: ...

@native_call([Arg(0), Addr(Arg(1))])
def pointer_to_values(
    values: Annotated[Float64[::], Aliased],
    use_values: Int32
) -> Annotated[Float64[:], Pointer, PointerAssociation("runtime"), Ownership("python"), Transfer("snapshot_copy"), Destruction("python_refcount")]: ...
