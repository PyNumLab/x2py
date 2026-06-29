---
title: First Wrapped Module
audience: users
prerequisites: first wrapped function
related: beginner-workflow.md, ../user-guide/wrapping-modules.md, ../language-support/feature-matrix.md
status: maintained
---

# First Wrapped Module

A Fortran module becomes a child Python module inside the extension. Public
procedures and supported public state appear on that child; private native
names and internal getter/setter hooks do not.

## Build The Checked Module-State Fixture

From the repository root:

```bash
python3 -m x2py tests/data/fortran/wrapper/fmodule_vars_f90.f90 \
  --wrap \
  --out-dir build/first-module \
  --json
```

The source stem creates extension `fmodule_vars_f90`. Its contained module is
available as `fmodule_vars_f90.fmodule_vars_f90`.

## Read Procedures And State

```python
import sys

import numpy as np

sys.path.insert(0, "build/first-module")
import fmodule_vars_f90

module = fmodule_vars_f90.fmodule_vars_f90

assert module.nmax == np.int32(12)
assert module.counter == np.int32(3)
assert module.scale == np.float64(1.5)
assert module.summarize() == np.int32(15)
```

The generated surface exposes public variable names directly. Internal native
helpers such as `get_counter` and `set_counter`, and private names such as
`hidden_counter`, are not part of the Python API.

## Mutate Module State

Writable state is assigned through the public attribute with its exact NumPy
dtype:

```python
module.counter = np.int32(9)
assert module.counter == np.int32(9)
assert module.summarize() == np.int32(21)

module.scale = np.float64(2.0)
assert module.scaled_counter() == np.float64(18.0)
```

Supported saved state is native process state. Importing a second extension
module object does not create a second copy of the underlying writable Fortran
state; updates are visible through both wrappers. Python-side values that are
not backed by a native setter can differ between module objects, so do not infer
native mutability from assignment success alone.

Procedure-local saved state also persists across calls:

```python
assert module.next_local() == np.int32(1)
assert module.next_local() == np.int32(2)
```

## Public Surface Rules

- The extension name comes from the first source filename.
- Each contained Fortran module is a Python child namespace.
- Public procedures use their generated Python names under that namespace.
- Supported writable module variables use direct attributes; generated native
  accessors stay hidden.
- Constants and parameters may be readable without a native setter.
- Private Fortran declarations remain absent from the public wrapper.

Use `--pyi` to inspect names and types before building:

```bash
python3 -m x2py tests/data/fortran/wrapper/fmodule_vars_f90.f90 --pyi
```

## Current Limitations

- Common-block procedure state is supported through procedures, but direct
  common-block variable exposure is not the public module-variable path.
- Allocatable module arrays have separate borrowing and lifetime rules; read
  [Allocatable Arrays](../user-guide/allocatable-arrays.md) before retaining a
  view across native reallocation.
- Exact dtype and ownership rules still apply to assignments.
- Unsupported module constructs remain listed in the
  [feature matrix](../language-support/feature-matrix.md).

If the extension imports but a name is absent, inspect the generated `.pyi`,
check native visibility, and use [Runtime Issues](../troubleshooting/runtime-issues.md).

## Evidence

The module attributes, hidden accessors, mutation, saved state, and repeated
import behavior are checked by
[`test_module_state.py`](../../tests/wrapper/fortran/module_state/test_module_state.py).
Generated module contracts are checked by
[`test_module_state_generated_pyi_contracts.py`](../../tests/wrapper/fortran/module_state/test_module_state_generated_pyi_contracts.py).
