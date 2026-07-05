from x2py.contracts import Addr, Annotated, Destruction, Float64, Int32, Ownership, Returns, Transfer

def scale_with_status(
    values: Annotated[
        Float64[:],
        Ownership("native"),
        Transfer("copy_return"),
        Destruction("native_owner"),
    ],
    status: Addr(Int32)
) -> Returns["values", Float64[:]]: ...
