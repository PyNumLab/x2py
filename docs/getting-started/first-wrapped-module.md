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
  --wrap \
  --out-dir build/first-module \
  --json
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
python3 -m x2py module_state.f90 --pyi
```

The generated package entry preserves the module namespace:

```python
from . import module_state
```

That entry file is Python export policy. In the advanced contract-editing
workflow, it can reshape exports without changing the native module leaf. To
try a small export edit, generate an editable package:

```bash
python3 -m x2py module_state.f90 --pyi --out contracts/module_state
```

Then edit `contracts/module_state/__init__.pyi` from the generated
namespace-preserving form:

```python
from . import module_state
```

to this explicit flattening form:

```python
from .module_state import *
```

Build the edited entry contract with the same native source:

```bash
python3 -m x2py contracts/module_state/__init__.pyi \
  --wrap \
  --native-fortran-sources module_state.f90 \
  --out module_state_flat \
  --out-dir build/module-state-flat
```

The resulting shared library exposes module procedures at the extension root:

```python
import sys

import numpy as np

sys.path.insert(0, "build/module-state-flat")
import module_state_flat

assert module_state_flat.summarize() == np.int32(15)
assert not hasattr(module_state_flat, "module_state")
```

You can also export only selected declarations, repeat an import, or expose the
same declaration under both its native Python name and an alias:

```python
from .module_state import counter
from .module_state import counter as current_count
from .module_state import summarize
```

That edited entry exposes `counter`, `current_count`, and `summarize` at the
extension root, while `scale`, `scaled_counter`, `saved_counter`, and
`next_local` stay out of the generated wrapper surface. After rebuilding that
entry contract with the same command, importing the shared library looks like
this:

```python
import sys

import numpy as np

sys.path.insert(0, "build/module-state-flat")
import module_state_flat

assert module_state_flat.counter == np.int32(3)
assert module_state_flat.current_count == np.int32(3)
assert module_state_flat.summarize() == np.int32(15)

module_state_flat.current_count = np.int32(9)
assert module_state_flat.counter == np.int32(9)
assert module_state_flat.summarize() == np.int32(21)

assert not hasattr(module_state_flat, "scale")
assert not hasattr(module_state_flat, "scaled_counter")
assert not hasattr(module_state_flat, "saved_counter")
assert not hasattr(module_state_flat, "next_local")
```

Both exported variable names route to the same native `counter` storage, but
they are not required to be the same Python object:

```python
assert module_state_flat.counter == module_state_flat.current_count
# Do not rely on: module_state_flat.counter is module_state_flat.current_count
```

These edits reshape Python exports only; they are not native ABI changes. Keep
the leaf contract as the source of native facts, and use
[Editing Semantic .pyi Contracts](../user-guide/editing-semantic-pyi-contracts.md)
when you are ready to edit the generated contract package.

The generated module leaf remains the native contract:

```python
nmax: Final[Int32] = 12

counter: Int32

scale: Float64

saved_counter: Int32

def summarize() -> Int32: ...

def scaled_counter() -> Float64: ...

def next_local() -> Int32: ...
```

A literal default on a mutable scalar module variable is an import-time native
initializer. For example, editing the leaf to:

```python
counter: Int32 = 41
```

keeps `counter` writable, but sets the native module storage when the extension
is imported:

```python
assert module_state_flat.counter == np.int32(41)
assert module_state_flat.summarize() == np.int32(53)

module_state_flat.counter = np.int32(5)
assert module_state_flat.summarize() == np.int32(17)
```

x2py applies that value through the generated native setter. The initializer
must be a literal value, not a Python call or expression.

Support boundaries for module state and other Fortran constructs are maintained
in the [language feature matrix](../language-support/feature-matrix.md).

If the extension imports but a name is absent, inspect the generated `.pyi`,
check native visibility, and use [Runtime Issues](../troubleshooting/runtime-issues.md).

## Evidence

The same module-state behavior, hidden accessors, mutation, saved state, and
repeated import behavior are checked by the internal fixture tests in
[`test_module_state.py`](../../tests/wrapper/fortran/module_state/test_module_state.py).
Generated module contracts are checked by
[`test_module_state_generated_pyi_contracts.py`](../../tests/wrapper/fortran/module_state/test_module_state_generated_pyi_contracts.py).
Edited entry export policy is checked by
[`test_pyi_wrapper_builds.py`](../../tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py).
