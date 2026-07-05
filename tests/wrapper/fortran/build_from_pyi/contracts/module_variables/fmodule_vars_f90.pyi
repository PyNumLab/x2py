from x2py.contracts import Final, Float64, Int32

nmax: Final[Int32] = 12

counter: Int32

scale: Float64

saved_counter: Int32

def summarize() -> Int32: ...

def scaled_counter() -> Float64: ...

def next_local() -> Int32: ...
