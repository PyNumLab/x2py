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

Derived-type parameters follow the same constant rule. A copy-safe
`Final[DerivedType]` is materialized as a wrapper-owned value copy and has no
native setter; it is not mutable native module storage and does not require an
`Aliased` annotation.

Public module variables already have module lifetime, whether or not `save` is
written explicitly. Procedure-local saved variables remain internal, but their
state persists across calls. Multiple imported Python module objects backed by
the same extension observe the same native module storage.

## Module Arrays

An allocatable module array is exposed as a persistent
`Allocatable[T[...]]` handle. Plain and `Aliased` declarations have the same
extraction behavior: a fresh `to_numpy()` call returns a live view of the
current allocation or `None`. `Aliased` preserves the native addressability
fact for other policy; it does not select view versus copy extraction. The
module attribute remains a handle even when native storage is unallocated:

```python
module.allocate_values(np.int32(3))
handle = module.values
assert handle.allocated is True
view = handle.to_numpy()
view[0] = np.float64(5.0)
```

Mutation through either kind of view reaches native module storage. A later
native deallocation or reallocation may make old views stale; accessing stale
views is unsupported and may crash. Use `view.copy()` first when Python needs
an independent lifetime. The same handle object then reports the new allocation
state.

Pointer-array module variables expose `Pointer[T[...]]` handles with a default
conservative operation policy. Association inspection and `nullify()` are
available by default. `to_numpy()` requires a completed extraction path, and
ownership-changing operations require explicit pointer policy.

## Derived Module Objects

A derived-type module variable is not automatically addressable just because
the same type can be constructed from Python. Python construction asks x2py to
allocate a new pointer-backed native instance. A pre-existing module variable
has its own source attributes. Both plain and `Aliased` declarations are read
as live generated objects, but their bridge mechanisms differ:

```python
from x2py.contracts import Aliased, Allocatable, Annotated, Float64

class box:
    values: Allocatable[Float64[:]]

current: Annotated[box, Aliased]
plain_current: box
```

Reading either attribute returns a native-owned live object. The wrapper never
copies or destroys module storage. `current` may use its proved native address;
`plain_current` uses typed module-specific bridge operations instead of
fabricating an address. Supported component access such as `.values` returns an
`Allocatable[T[...]]` handle retaining the object; call `to_numpy()` to obtain
its current view.

Whole object replacement through `module.current = other` is not exposed.
Mutate live native module state through its completed module-object policy or a
wrapped native procedure. Use `.copy()` on an extracted array view when
independent NumPy storage is required.

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
- Pointer state is exposed only when association, target lifetime, and a live
  descriptor-view mechanism are complete; there is no detached-copy fallback.
- Plain and `Aliased` derived-type module variables both use the live generated
  object surface. Plain objects require complete typed member operations;
  `Aliased` objects may use a direct native address. Unsupported members block
  generation instead of changing the public representation.
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
