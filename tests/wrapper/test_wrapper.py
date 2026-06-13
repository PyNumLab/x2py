# run python3 ../../semantics/asr_to_ast.py caxpy.f
import caxpy
import numpy as np
a = np.float32(2.)
assert caxpy.SQUARE(a) == a**2
print("TEST PASSING!!")

