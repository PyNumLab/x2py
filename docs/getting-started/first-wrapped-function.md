---
title: First Wrapped Function
audience: users
prerequisites: installation, verification
related: first-wrapped-module.md, ../user-guide/wrapping-functions.md, ../reference/semantic-pyi-format.md
status: maintained
---

# First Wrapped Function

This example builds one checked scalar function and calls it with the exact
NumPy dtypes required by its native contract.

## Source

Use the repository fixture below, or place the same standalone function in your
project.

<!-- x2py-doc-source: tests/data/fortran/wrapper/scale.f90 -->
```fortran
real(8) function scale(value, factor) result(output)
  real(8), intent(in) :: value
  real(8), intent(in) :: factor
  output = value * factor
end function scale
```

The generated Python call accepts two `numpy.float64` values and returns a
`numpy.float64` result.

## Build

From the repository root:

```bash
python3 -m x2py tests/data/fortran/wrapper/scale.f90 \
  --wrap \
  --out-dir build/first-function \
  --json
```

The extension is named after the source stem: `scale`. The standalone native
function is exposed directly at that extension's root.

## Import And Call

```python
import sys

import numpy as np

sys.path.insert(0, "build/first-function")
import scale

result = scale.scale(np.float64(3.0), np.float64(2.5))

assert isinstance(result, np.float64)
assert result == np.float64(7.5)
```

The checked call returns `numpy.float64(7.5)`.

## Inspect The Generated Signature

Before compiling, print the semantic contract:

```bash
python3 -m x2py tests/data/fortran/wrapper/scale.f90 --pyi
```

The generated declaration is:

```python
@external
def scale(
    value: Ptr(Const(Float64)),
    factor: Ptr(Const(Float64))
) -> Float64: ...
```

The contract describes `value` and `factor` as pointers to constant `Float64`
values and the function result as `Float64`. The semantic `.pyi` is a native
contract, not an ordinary pure-Python type stub. Read
[Semantic .pyi Format](../reference/semantic-pyi-format.md) before editing it.

## Failure Mode: Wrong Scalar Type

Native scalar arguments use exact NumPy dtypes. A plain Python `float` is not a
replacement for `numpy.float64` at this boundary:

```python
scale.scale(3.0, 2.5)  # raises TypeError
```

Do not fix this by adding an implicit conversion inside generated code. Convert
at the Python call site so the selected ABI is explicit:

```python
scale.scale(np.float64(3.0), np.float64(2.5))
```

For array functions, rank, dtype, shape, order, contiguity, and allowed stride
patterns can also be contract requirements. Continue with
[Wrapping Functions](../user-guide/wrapping-functions.md) and
[Arrays](../user-guide/arrays.md). The central
[language feature matrix](../language-support/feature-matrix.md) records
supported, partial, and unsupported wrapper forms.

Build failures go to [Build Issues](../troubleshooting/build-issues.md); a
successful import followed by a call failure goes to
[Runtime Issues](../troubleshooting/runtime-issues.md).

## Evidence

The displayed source is checked against the repository fixture by
[`test_documentation_examples.py`](../../tests/tools/test_documentation_examples.py).
The renamed extension and `7.5` runtime result are checked by
[`test_build_modes.py`](../../tests/wrapper/fortran/build_from_source/test_build_modes.py).
