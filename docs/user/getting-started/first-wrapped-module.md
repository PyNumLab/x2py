---
title: First Wrapped Module
audience: users
prerequisites: first wrapped function
related: beginner-workflow.md, ../guide/wrapping-modules.md, ../language-support/feature-matrix.md
status: maintained
---

# First Wrapped Module

A Fortran module becomes a child Python module inside the extension. Public
procedures and supported public state appear on that child; private native
names and internal getter/setter hooks do not.

## Source

Create `module_state.f90` with this module:

```fortran
module module_state
  implicit none
  private
  public :: nmax, counter, scale, saved_counter
  public :: summarize, scaled_counter, next_local

  integer(4), parameter :: nmax = 12
  integer(4) :: counter = 3
  real(8) :: scale = 1.5d0
  integer(4), save :: saved_counter = 6
  integer(4) :: hidden_counter = 17

contains
  integer(4) function summarize() result(value)
    value = counter + nmax
  end function summarize

  real(8) function scaled_counter() result(value)
    value = real(counter, 8) * scale
  end function scaled_counter

  integer(4) function next_local() result(value)
    integer(4), save :: local_counter = 0

    local_counter = local_counter + 1
    value = local_counter
  end function next_local
end module module_state
```

## Build

From the directory containing `module_state.f90`:

```bash
python3 -m x2py module_state.f90 \
  --out-dir build/first-module
```

The source stem creates extension `module_state`. Its contained module is
available as `module_state.module_state`.

## Read Procedures And State

```python
import sys

import numpy as np

sys.path.insert(0, "build/first-module")
import module_state

module = module_state.module_state

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
python3 -m x2py generate --pyi module_state.f90
```

The generated package entry preserves the module namespace:

```python
from . import module_state
```

The generated module leaf remains the native contract:

```python
from x2py.contracts import Final, Float64, Int32

nmax: Final[Int32] = 12

counter: Int32

scale: Float64

saved_counter: Int32

def summarize() -> Int32: ...

def scaled_counter() -> Float64: ...

def next_local() -> Int32: ...
```

The entry file is Python export policy. Advanced contract editing can flatten
the child module, select only some declarations, or expose one native declaration
under multiple Python names. Those edits reshape Python exports only; they are
not native ABI changes. Keep the leaf contract as the source of native facts and
wait for Editing Semantic `.pyi` Contracts later in the User Guide before
changing the generated contract package.

The language feature matrix later collects support boundaries for module state
and other Fortran constructs.

If the extension imports but a name is absent, inspect the generated `.pyi`,
then check native visibility. Runtime Issues later expands this diagnosis.

## Evidence

The same module-state behavior, hidden accessors, mutation, saved state, and
repeated import behavior are checked by the internal fixture tests in
[`test_module_state.py`](../../../tests/wrapper/fortran/module_state/test_module_state.py).
Generated module contracts are checked by
[`test_module_state_generated_pyi_contracts.py`](../../../tests/wrapper/fortran/module_state/test_module_state_generated_pyi_contracts.py).
The advanced entry export policy linked from this page is checked by
[`test_pyi_wrapper_builds.py`](../../../tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py).
