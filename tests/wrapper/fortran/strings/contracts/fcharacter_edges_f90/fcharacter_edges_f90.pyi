@native_call([Arg(0)])
def fixed_inout(
    name: Ref(String[8])
) -> Returns["name", Ref(String[8])]: ...

@native_call([Arg(0)])
def assumed_inout(
    name: Ref(String)
) -> Returns["name", Ref(String)]: ...

@native_call([Arg(0)])
def optional_inout(
    label: Ref(String) = ...
) -> Returns["label", Ref(String), Optional]: ...

@native_call([Return('label', 0)])
def make_out() -> String[6]: ...

def unicode_echo(
    label: Ref(Const(String))
) -> String[5]: ...
