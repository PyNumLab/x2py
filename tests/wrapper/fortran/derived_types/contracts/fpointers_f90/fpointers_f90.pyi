@native_call([Ref(Arg(0))])
def read_pointer(
    value: Annotated[Const(Float64), PointerAssociation("runtime")]
) -> Float64: ...

@native_call([Ref(Arg(0)), Ref(Arg(1))])
def pointer_to_scalar(
    value: Annotated[Const(Float64), FortranTarget],
    use_value: Const(Int32)
) -> Annotated[Ref(Float64), PointerAssociation("runtime")]: ...

def sum_pointer(
    values: Annotated[Const(Float64[:]), Pointer, PointerAssociation("runtime")]
) -> Float64: ...

@native_call([Arg(0), Ref(Arg(1))])
def pointer_to_values(
    values: Annotated[Const(Float64[::Strided]), FortranTarget],
    use_values: Const(Int32)
) -> Annotated[Float64[:], Pointer, PointerAssociation("runtime")]: ...
