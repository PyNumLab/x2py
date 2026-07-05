from x2py.contracts import Allocatable, Annotated, Int32, Optional, Returns, String

def string_len_assumed(
    text: String
) -> Int32: ...

def string_len_fixed(
    text: String[8]
) -> Int32: ...

def fixed_array_extent(
    labels: String[8][:]
) -> Int32: ...

def replace_names(
    names: Annotated[String[:][:], Allocatable]
) -> Returns[
    "names", Annotated[String[:][:], Allocatable], Optional
]: ...

def rewrite_storage(
    label: String[8][()]
) -> None: ...
