---
title: x2py
audience: users
prerequisites: none
related: user/getting-started/index.md, user/getting-started/installation.md
status: maintained
publication: reviewed
---

# x2py

x2py turns supported Fortran source into an importable Python extension. It
also exposes the parsed interface as language-neutral semantic IR and editable
`.pyi` contracts, so unsupported boundaries are reported before wrapper code is
compiled.

## Try x2py

This first example wraps a scalar Fortran function. Create `scale.f90`:

<!-- x2py-doc-source: tests/data/fortran/wrapper/scale.f90 -->
```fortran
real(8) function scale(value, factor) result(output)
  real(8), intent(in) :: value
  real(8), intent(in) :: factor
  output = value * factor
end function scale
```

Build the Python extension from the directory containing that file:

```bash
python3 -m x2py scale.f90
```

The command creates an importable `scale` extension beside the source and keeps
its generated wrapper and build artifacts under `__x2py__/`. Call the native
function from Python with the exact NumPy scalar types required by its
contract:

```python
import numpy as np

import scale

result = scale.scale(np.float64(3.0), np.float64(2.5))
print(result)
```

The call prints:

```text
7.5
```

The generated function is inspectable from Python:

```python
print(scale.scale.__doc__)
```

Its docstring describes the public signature, accepted dtypes, result, and
call-time type error:

```text
scale(value, factor) -> float64

Parameters
----------
value : float64
factor : float64

Returns
-------
result : float64

Raises
------
TypeError
    If an argument has an incompatible Python type or dtype.
```

That is the basic x2py workflow: provide native source, build an extension,
import it, and call the generated Python surface.

## Continue With Getting Started

This preview assumes x2py, NumPy, and a supported native compiler are already
available. [Getting Started](user/getting-started/index.md) walks through
installation and verification first, then rebuilds this function and explains
its generated contract and artifacts.
