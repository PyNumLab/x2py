def read_pointer(
    value: Annotated[Ptr(Const(Float64)), PointerAssociation("runtime")]
) -> Float64: ...

def pointer_to_scalar(
    value: Annotated[Ptr(Const(Float64)), FortranTarget],
    use_value: Ptr(Const(Int32))
) -> Annotated[Ptr(Float64), PointerAssociation("runtime")]: ...

def sum_pointer(
    values: Annotated[Const(Float64[:]), Pointer, PointerAssociation("runtime")]
) -> Float64: ...

def pointer_to_values(
    values: Annotated[Const(Float64[::Strided]), FortranTarget],
    use_values: Ptr(Const(Int32))
) -> Annotated[Float64[:], Pointer, PointerAssociation("runtime")]: ...
