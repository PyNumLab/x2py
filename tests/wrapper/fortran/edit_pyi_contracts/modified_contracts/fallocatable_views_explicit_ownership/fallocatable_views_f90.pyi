# Intentional difference: the three array contexts state their complete owner,
# boundary-transfer, and destruction policy explicitly.
class buffer:
    def __init__(
        self,
        *,
        values: Annotated[
            Float64[:],
            Allocatable,
            Ownership("wrapper"),
            Transfer("borrowed_view"),
            Destruction("wrapper_dealloc"),
        ] = ...
    ) -> None: ...

    values: Annotated[
        Float64[:],
        Allocatable,
        Ownership("wrapper"),
        Transfer("borrowed_view"),
        Destruction("wrapper_dealloc"),
    ]

    def allocate_values(
        self,
        n: Ref(Const(Int32))
    ) -> None: ...

    def deallocate_values(self) -> None: ...

    def scale_values(
        self,
        scale: Ref(Const(Float64))
    ) -> None: ...

    def values_sum(self) -> Float64: ...

module_values: Annotated[
    Float64[:],
    Allocatable,
    Aliased,
    Ownership("native"),
    Transfer("borrowed_view"),
    Destruction("native_owner"),
] | None

def allocate_module_values(
    n: Ref(Const(Int32))
) -> None: ...

def deallocate_module_values() -> None: ...

def module_values_sum() -> Float64: ...

@native_call([Arg(0), Return('values', 0)])
def build_values(
    n: Ref(Const(Int32))
) -> Annotated[
    Float64[:],
    Allocatable,
    Ownership("python"),
    Transfer("copy_return"),
    Destruction("python_refcount"),
] | None: ...
