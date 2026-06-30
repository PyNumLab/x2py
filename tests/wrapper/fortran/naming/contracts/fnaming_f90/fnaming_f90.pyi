class visible_t:
    def __init__(
        self,
        *,
        lambda_: Annotated[Int32, Name("lambda")] = 3,
        lambda__2: Annotated[Int32, Name("lambda_")] = 4
    ) -> None: ...

    lambda_: Annotated[Int32, Name("lambda")] = 3
    lambda__2: Annotated[Int32, Name("lambda_")] = 4

    @bind("visible_from")
    def from_(self) -> Int32: ...

value: Int32

@bind("lambda")
@native_call([Ref(Arg(0))])
def lambda_(
    value: Const(Int32)
) -> Int32: ...

@bind("lambda_")
@native_call([Ref(Arg(0))])
def lambda__2(
    value: Const(Int32)
) -> Int32: ...

def get_value() -> Int32: ...
