def scale_with_status(
    values: Annotated[
        Float64[:],
        Ownership("native"),
        Transfer("copy_return"),
        Destruction("native_owner"),
    ],
    status: Annotated[Ref(Int32), Intent("out")]
) -> Returns["values", Float64[:]]: ...
