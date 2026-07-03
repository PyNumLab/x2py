---
title: Wrapping Functions
audience: users
prerequisites: data types, first wrapped function
related: wrapping-subroutines.md, arrays.md, fortran-wrapper.md
status: maintained
---

# Wrapping Functions

A Fortran `function` becomes a Python callable. The direct result of the function becomes the first returned value in Python. 
All arguments follow the exact semantic types shown in the generated `.pyi` file.

See [Data Types](data-types.md) for details on how Fortran types are mapped to Python/NumPy.

For this example, we'll use `scale.f90` (from [README Quick Start](../../README.md#quick-start)).

```bash
python3 -m x2py scale.f90 --pyi
python3 -m x2py scale.f90 --wrap-readiness
python3 -m x2py scale.f90 --out-dir build/scale
```

## Scalar Functions

The generated contract for the scale function is:

```python
@external
@native_call([Addr(Arg(0)), Addr(Arg(1))])
def scale(
    value: Const(Float64),
    factor: Const(Float64),
) -> Float64: ...
```

Call it like this:

```python
result = scale.scale(np.float64(3.0), np.float64(2.5))
assert result == np.float64(7.5)
```

Contained module functions appear on their generated child module instead of
the extension root. Standalone procedures carry `@external` in the semantic
contract. These placement details do not change the Python argument types.

Supported scalar function results include resolved signed integer, real,
complex, logical, scalar character, and supported derived-type values. Read
[Data Types](data-types.md) for the complete mapping. Scalar character results
are Python-owned `str` values; derived results are wrapper-owned generated
class instances.

## Array Results

Functions can return numeric arrays. These are returned as new NumPy arrays with Fortran (column-major) ordering.

Example (`function_results.f90`):

```fortran
module results
  implicit none
contains
  function squares(size) result(values)
    integer(4), intent(in) :: size
    real(8) :: values(size)
    integer(4) :: index

    values = [(real(index, 8) * real(index, 8), index = 1, size)]
  end function squares
end module results
```

Generated contract:

```python
@native_call([Addr(Arg(0))])
def squares(
    size: Const(Int32)
) -> Float64[size]: ...
```

Build it:

```bash
python3 -m x2py function_results.f90 --out-dir build/function-results
```

Usage:

```python
import sys
import numpy as np

sys.path.insert(0, "build/function-results")
import function_results

api = function_results.results
result = api.squares(np.int32(4))

np.testing.assert_array_equal(
    result,
    np.array([1.0, 4.0, 9.0, 16.0], dtype=np.float64),
)
```

Allocated zero-sized results are zero-sized arrays. An unallocated allocatable
result or unassociated pointer result is `None`. Multidimensional results retain
Fortran-oriented element ordering. See [Arrays](arrays.md) for broader array
validation and [Allocatable Arrays](allocatable-arrays.md) before relying on
result lifetime.

## Functions With Output Arguments

If a function also has output arguments, Python returns a tuple: **first the direct function result, then the output arguments** in their native
argument order.

Create `function_outputs.f90`:

```fortran
module outputs
  implicit none
contains
  function sum_with_count(values, count) result(total)
    real(8), intent(in) :: values(:)
    integer(4), intent(out) :: count
    real(8) :: total

    total = sum(values)
    count = size(values)
  end function sum_with_count
end module outputs
```

Inspecting `function_outputs.f90` prints this function contract:

```python
@native_call([Arg(0), Return('count', 1)])
def sum_with_count(
    values: Const(Float64[::])
) -> tuple[Float64, Int32]: ...
```

Build it:

```bash
python3 -m x2py function_outputs.f90 --out-dir build/function-outputs
```

Then assert the tuple order:

```python
import sys

import numpy as np

sys.path.insert(0, "build/function-outputs")
import function_outputs

api = function_outputs.outputs
source = np.array([4.0, -2.0, 7.0], dtype=np.float64)
total, count = api.sum_with_count(source)
assert total == np.float64(9.0)
assert count == np.int32(3)
```

Caller-provided output arrays remain arguments because the caller must allocate
their storage. Their return projection, when present, refers to that same
object. The same `intent(out)` and `intent(inout)` projection rules apply to
subroutines that have no direct function result.

## Call Limits

- Exact input dtype is required where the generated contract names one; x2py
  does not silently narrow or widen a native scalar or array.
- Numeric and fixed-width bytes character array results support ranks 1 through
  15. Arrays of derived types are blocked.
- Wider-than-supported real, complex, or explicit logical storage is blocked
  rather than narrowed.
- A function result never creates an unproven borrowed pointer view.
- Native `stop`, `error stop`, or process abort cannot be converted into a
  normal Python return.

## Evidence And Troubleshooting

Scalar calls are exercised by
[`test_verified_baseline.py`](../../tests/wrapper/fortran/scalars/test_verified_baseline.py),
array results by
[`test_array_results.py`](../../tests/wrapper/fortran/arrays/test_array_results.py),
and mixed result projection by
[`test_output_arguments.py`](../../tests/wrapper/fortran/function_calls/test_output_arguments.py).

For a rejected Python value, compare it with generated `.pyi` output and use
[Runtime Issues](../troubleshooting/runtime-issues.md). For a readiness blocker,
check the [feature matrix](../language-support/feature-matrix.md) before trying
to compile.
