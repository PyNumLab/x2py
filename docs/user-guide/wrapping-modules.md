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

The checked beginner example builds source `module_state.f90` as extension
`module_state` and imports its contained module as:

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

For several ordered sources, one generated extension can contain several child
modules. Each native module retains its own child namespace, while standalone
procedures remain on the extension root. The first source determines the
default extension name unless `--out` selects another name.

## Public Variables

Supported public scalar integer, real, complex, and logical module variables
are direct Python attributes. Reading fetches current native state and assigning
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
nmax: Final[Int32] = 12
```

No native setter exists for a parameter. Assigning `module.nmax` in Python can
only shadow the attribute on that Python module object; it does not mutate the
native parameter.

Public module variables already have module lifetime, whether or not `save` is
written explicitly. Procedure-local saved variables remain internal but their
state persists across calls. Multiple imported Python module objects backed by
the same extension observe the same native module storage.

## Module Arrays

A supported target-backed allocatable module array is a native-owned borrowed
view or `None` when unallocated:

```python
module.allocate_values(np.int32(3))
view = module.values
view[0] = np.float64(5.0)
```

Mutation reaches native module storage. A later native deallocation or
reallocation invalidates old views; use `view.copy()` first when Python needs an
independent lifetime. Pointer module variables use snapshot-or-block policy.

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
- Pointer state is exposed only when snapshot policy is complete; general
  borrowed pointer variables are blocked.
- Source ordering and external dependency discovery remain the caller's job.

## Evidence And Troubleshooting

Module variables, constants, saved state, visibility, and shared native state
are exercised by
[`test_module_state.py`](../../tests/wrapper/fortran/module_state/test_module_state.py).
Common-block procedure behavior is exercised by
[`test_common_blocks.py`](../../tests/wrapper/fortran/module_state/test_common_blocks.py).

Use [Memory Management](memory-management.md) before retaining module array
views, and [Runtime Issues](../troubleshooting/runtime-issues.md) for import,
attribute, or shared-state problems.
