---
title: First Wrapped Function
audience: users
prerequisites: installation, verification
related: first-wrapped-module.md, ../guide/wrapping-functions.md, ../reference/semantic-pyi-format.md
status: maintained
---

# First Wrapped Function

This example builds one checked scalar function and calls it with the exact
NumPy dtypes required by its native contract.

## Source

Reuse the same `scale.f90` input from the
[README Quick Start](../../../README.md#quick-start).

The generated Python call accepts two `numpy.float64` values and returns a
`numpy.float64` result.

## Build

From the directory containing `scale.f90`:

```bash
python3 -m x2py scale.f90 \
  --out-dir build/first-function
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
python3 -m x2py scale.f90 --pyi
```

The generated declaration is:

```python
from x2py.contracts import Addr, Arg, Float64, external, native_call

@external
@native_call([Addr(Arg(0)), Addr(Arg(1))])
def scale(
    value: Float64,
    factor: Float64
) -> Float64: ...
```

The contract describes `value` and `factor` as read-only `Float64` values at
the Python boundary. The `@native_call` decorator records that the native call
receives the address of each converted native scalar slot. It does not mean the
caller passes references. The semantic `.pyi` is a native contract, not an
ordinary pure-Python type stub. Do not edit it during this first workflow; the
Semantic `.pyi` Format reference explains the complete grammar later.

Fortran `intent` is not printed into the semantic `.pyi`. It helps generate the
initial Python argument/result projection, but the visible signature,
`Returns[...]`, and ordered `@native_call` list are the wrapper authority after
the contract is loaded. The compiled Fortran procedure retains its own `intent`.

## Failure Mode: Wrong Scalar Type

Native scalar arguments use exact NumPy dtypes. A plain Python `float` is not a
replacement for `numpy.float64` at this boundary:

```python
from x2py.contracts import raises

scale.scale(3.0, 2.5)  # raises TypeError
```

Do not fix this by adding an implicit conversion inside generated code. Convert
at the Python call site so the selected ABI is explicit:

```python
scale.scale(np.float64(3.0), np.float64(2.5))
```

For array functions, rank, dtype, shape, order, contiguity, and allowed stride
patterns can also be contract requirements. Wrapping Functions and Arrays
expand those rules later in the User Guide. The language feature matrix later
records supported, partial, and unsupported wrapper forms.

Build Issues and Runtime Issues are covered later in Troubleshooting. For now,
rerun failed builds with `--verbose`, and compare rejected calls with the
generated `.pyi` contract.

## Evidence

The linked `scale.f90` input is checked against the repository fixture by
[`test_documentation_examples.py`](../../../tests/docs/test_examples.py).
The default extension name and `7.5` runtime result are checked by
[`test_build_modes.py`](../../../tests/wrapper/fortran/build_from_source/test_build_modes.py).
