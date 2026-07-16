---
title: Memory Management
audience: users, advanced users
prerequisites: arrays, wrapping derived types
related: allocatables.md, pointers.md, editing-semantic-pyi-contracts.md
status: maintained
---

# Memory Management

Ownership determines whether Python sees a value, copy, live view, or generated
native object; whether mutation reaches native storage; and which runtime is
responsible for destruction. x2py completes these decisions before wrapper
generation. Bridge and binding code consume the completed policy and do not
guess from datatype or intent.

## Ownership Vocabulary

| Owner or transfer | Meaning | First complete example |
| --- | --- | --- |
| Python-owned value or copy | Python or NumPy releases detached storage after references are gone. | an ordinary array function result or `.copy()` of an extracted view |
| Caller-owned storage | The Python caller retains the exact object supplied to the call. | [`outputs.f90` output array](wrapping-subroutines.md#complete-output-example) |
| Wrapper-owned instance | A generated Python extension object owns one native derived instance. | [`points.f90` result](wrapping-derived-types.md#complete-derived-type-example) |
| Native-owned storage | Native module state or another native owner controls allocation and release. | [`allocations.f90` module handle](allocatables.md#complete-allocatable-example) |
| Borrowed view or child | Python refers to storage owned by a module or containing wrapper. | [`points.f90` nested child](wrapping-derived-types.md#complete-derived-type-example) |
| Detached copy (`snapshot_copy` policy) | Python receives copied current native state where an explicit value-copy policy requires it. Native-array-handle `to_numpy()` and derived module-object reads do not select this behavior. | Explicit copy-result contracts |
| Call-local association | Native code may refer to Python storage only during one wrapped call. | [`pointers.f90` input](pointers.md#complete-pointer-example) |

Those linked pages contain the full source, build commands, and asserted
results. The examples are not repeated here so ownership differences remain
attached to one canonical source listing.

## Core Invariants

1. Exactly one owner destroys each owned native allocation.
2. Python-owned copies are independent of later native mutation.
3. Caller-owned arrays are never freed by x2py.
4. A borrowed child or component view retains its generated wrapper owner.
5. Owner retention does not protect a view from explicit native reallocation or deallocation.
6. A pointer declaration never proves ownership of its target.
7. Missing owner, lifetime, release, shape, dtype, mutability, nullability, or aliasing facts block generation.
8. Addressability is an object-origin fact: generated constructors allocate
   pointer-backed instances, while pre-existing derived module objects need
   either proved `Aliased` addressability or typed module-specific bridge
   operations. A backend must not fabricate an address.
9. Native array descriptor state lives in `Allocatable[T[...]]` and
   `Pointer[T[...]]` handles; borrowed NumPy views and detached NumPy copies are
   explicit extraction results from `to_numpy()`.

## Destruction Responsibilities

| Value | Release responsibility |
| --- | --- |
| scalar, string, copy-return array, scalar pointer copied value | Python, NumPy, or its generated base capsule |
| caller-supplied NumPy array | Python caller |
| wrapper-owned derived instance | generated wrapper deallocator and native finalization |
| borrowed nested component | containing wrapper owner |
| allocatable or pointer array handle | containing wrapper, native module, or explicit x2py owner storage |
| borrowed view extracted from a handle | the handle's completed owner policy |
| call-local temporary | generated bridge before return |
| pointer target | explicit proved owner, never the pointer declaration alone |

Users do not call a generated `destroy()` method for ordinary wrapper-owned
objects. Explicit native allocation and deallocation routines remain normal
wrapped calls, but using one can invalidate previously borrowed storage.

## Copies Versus Views

Use a copy when Python needs an independent lifetime:

```python
independent = borrowed_view.copy()
```

This operation is ordinary NumPy behavior applied after obtaining the view from
the complete `allocations.f90` example. It is the safe boundary before a native
operation that may reallocate or deallocate the authoritative storage.

Do not use `del view` as a native deallocation mechanism. Releasing a borrowed
Python object only releases the view and any owner-retaining Python reference;
it does not transfer native release responsibility.

## Mutability And Replacement

- Ordinary caller-owned arrays **mutate in place**;
- Python strings use **replacement** because `str` is immutable;
- Allocatable array descriptors use **handles** because native allocation identity may change;
- Ordinary non-descriptor array/function results use **copy-return**;
- Allocatable array results use wrapper-owned handles whose finalizer releases
  x2py-owned descriptor storage;
- Pointer-array handle results block readiness until owner storage, target
  lifetime, descriptor extraction, and destroy behavior are implemented;
- plain and `Aliased` derived module variables remain live native-owned objects
  through module-specific or address-backed mechanisms respectively; and
- Borrowed views extracted from handles **share native storage** until native
  invalidation.

Native-array-handle extraction remains live-view-or-`None`; callers use
`.copy()` on an extracted NumPy view for independent array storage.

Return projection and ownership are one contract. An edited `.pyi` cannot ask
for copy-return without a projected replacement, or combine immutable storage
with a writable borrowed view.

## Policy Source Of Truth

Generated source facts enter semantic IR, then post-IR policy completion chooses
object kind, ownership, transfer, destruction, mutability, nullability, output
projection, release responsibility, storage mode, getter behavior, native
setter assignment, and Python setter exposure. Unsupported or contradictory
combinations stop before wrapper lowering.

Advanced users can inspect or edit explicit `Ownership(...)`, `Transfer(...)`,
and `Destruction(...)` metadata. Editing Semantic `.pyi` Contracts and the
semantic format reference explain the editable forms later. Metadata can select
an implemented policy; it cannot invent a backend path.

## Evidence And Troubleshooting

The same array concept under native-owned, wrapper-owned, and Python-owned
lifetimes is exercised by
[`test_ownership_contracts.py`](../../../tests/wrapper/fortran/edit_pyi_contracts/test_ownership_contracts.py).
Exactly-once wrapper finalization is exercised by
[`test_borrowed_finalizers.py`](../../../tests/wrapper/fortran/derived_types/test_borrowed_finalizers.py).

Treat use-after-deallocation risk as an application lifetime bug, not a signal
to guess ownership. Copy before native reallocation. Runtime Issues later
covers reproducible lifetime or cleanup symptoms.
