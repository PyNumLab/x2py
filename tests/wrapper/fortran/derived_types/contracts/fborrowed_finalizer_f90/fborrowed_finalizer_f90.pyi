@native_type(finalizers=('cleanup_child',))
class child:
    pass

class parent:
    value: child

def get_final_count() -> Int32: ...

def reset_final_count() -> None: ...
