@native_call([Arg(0)])
def fixed_inout(
    name: Ptr(String[8])
) -> Returns["name", Ptr(String[8])]: ...

@native_call([Arg(0)])
def assumed_inout(
    name: Ptr(String)
) -> Returns["name", Ptr(String)]: ...

@native_call([Arg(0)])
def optional_inout(
    label: Ptr(String) = ...
) -> Returns["label", Ptr(String), Optional]: ...

@native_call([Return('label', 0)])
def make_out() -> String[6]: ...

def unicode_echo(
    label: Ptr(Const(String))
) -> String[5]: ...
