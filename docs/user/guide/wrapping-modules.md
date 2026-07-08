---
title: Wrapping Modules
audience: users
prerequisites: data types, first wrapped module
related: wrapping-functions.md, memory-management.md, packaging.md
status: maintained
---

# Wrapping Modules

A contained Fortran module becomes a child Python module inside the generated
extension. Standalone procedures stay at the extension root. x2py preserves
this namespace instead of flattening native module membership implicitly.

As seen in the introductory example, building the source file `module_state.f90`
creates an extension named module_state, allowing you to import its contained module:

```python
import module_state

module = module_state.module_state
```

See [First Wrapped Module](../getting-started/first-wrapped-module.md) for the
complete source, build command, generated contract, and checked calls.

## Procedures And Package Shape

Module functions and subroutines are attributes of the child module:

```python
assert module.summarize() == np.int32(15)
```

When compiling multiple ordered source files, a single generated extension can contain multiple child modules.
Each native module retains its own child namespace, while standalone
procedures remain on the extension root. The first source determines the
default extension name unless `--out` selects another name.

## Public Variables

Supported public scalar integer, real, complex, and logical module variables
are direct Python attributes. Reading fetches its current native state, and assigning
an exact matching value writes through to native storage:

```python
module.counter = np.int32(9)
assert module.counter == np.int32(9)
assert module.summarize() == np.int32(21)
```

Generated getter and setter bridge routines are internal and do not appear as
Python callables. Private variables are omitted.

## Constants And Saved State

Representable native parameters become `Final[...]` constants in the generated
contract:

```python
from x2py.contracts import Final, Int32

nmax: Final[Int32] = 12
```

No native setter exists for a parameter. Assigning `module.nmax` in Python can
only shadow the attribute on that Python module object; it does not mutate the
native parameter.

Public module variables already have module lifetime, whether or not `save` is
written explicitly. Procedure-local saved variables remain internal, but their
state persists across calls. Multiple imported Python module objects backed by
the same extension observe the same native module storage.

## Module Arrays

An `Aliased` allocatable module array is a native-owned borrowed view or
`None` when unallocated. A plain allocatable module array returns a read-only
snapshot copy instead:

```python
module.allocate_values(np.int32(3))
view = module.values
view[0] = np.float64(5.0)
```

For aliased arrays, mutation reaches native module storage. A later native
deallocation or reallocation invalidates old views; use `view.copy()` first when
Python needs an independent lifetime. Pointer-array module variables have a
default conservative handle policy, but generated descriptor-handle accessors
are still a readiness blocker.

## Derived Module Objects

A derived-type module variable is not automatically addressable just because
the same type can be constructed from Python. Python construction asks x2py to
allocate a new pointer-backed native instance. A pre-existing module variable
has its own source attributes. `Aliased` on that declaration selects a live
borrowed wrapper:

```python
from x2py.contracts import Aliased, Allocatable, Annotated, Float64

class box:
    values: Allocatable[Float64[:]]

current: Annotated[box, Aliased]
```

Reading `module.current` returns a native-owned borrowed wrapper. The wrapper
does not copy or destroy `current`; it retains the module object's address and
allows supported component access such as `module.current.values`.
An allocatable component view is writable and reaches native module state until
native code reallocates or deallocates that component.

Without `Aliased` or another completed live-borrow policy, x2py blocks the
plain derived module variable before wrapper lowering. Whole-object
`Snapshot[T]` contracts are future-only; the active contract does not generate
or accept them as a detached fallback.

Whole object replacement through `module.current = other` is not exposed.
Mutate native module state through an `Aliased` borrowed object or a wrapped
native procedure, then read a new snapshot when Python needs a detached copy.

## Common Blocks

Common-block storage is not exported as Python variables. Wrapped procedures
may still read and write common-block state, so the supported surface is the
native procedure API:

```python
module.write_shared(np.int32(17))
assert module.read_shared() == np.int32(17)
```

x2py does not add locking around module state. The caller remains responsible
for synchronization across Python threads, OpenMP workers, or external native
code.

## Limitations

- Private module declarations remain hidden.
- Common-block variables have no generated attribute surface.
- Pointer state is exposed only when detached-copy policy is complete; general
  borrowed pointer variables are blocked.
- Plain derived-type module variables are exposed only when the recursive
  snapshot policy covers every field; `Aliased` is required for live borrowing.
- Source ordering and external dependency discovery remain the caller's job.

## Evidence And Troubleshooting

Module variables, constants, saved state, visibility, and shared native state
are exercised by
[`test_module_state.py`](../../../tests/wrapper/fortran/module_state/test_module_state.py).
Common-block procedure behavior is exercised by
[`test_common_blocks.py`](../../../tests/wrapper/fortran/module_state/test_common_blocks.py).

Module array views remain native-owned and can become stale after native
reallocation or deallocation; copy data that needs an independent lifetime.
Memory Management later expands that ownership rule, and Runtime Issues later
covers import, attribute, and shared-state problems.
