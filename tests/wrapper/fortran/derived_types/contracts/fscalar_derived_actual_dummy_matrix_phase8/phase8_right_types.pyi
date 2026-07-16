from x2py.contracts import Int32


class item:
    value: Int32


def make_item(initial: Int32) -> item: ...
