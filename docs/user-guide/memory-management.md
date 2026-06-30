---
title: Memory Management
audience: users, advanced users
prerequisites: arrays, wrapping derived types
related: allocatable-arrays.md, pointer-arguments.md, editing-semantic-pyi-contracts.md
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
| Python-owned value or copy | Python or NumPy releases detached storage after references are gone. | [`allocations.f90` copy result](allocatable-arrays.md#complete-allocatable-example) |
| Caller-owned storage | The Python caller retains the exact object supplied to the call. | [`outputs.f90` output array](wrapping-subroutines.md#complete-output-example) |
| Wrapper-owned instance | A generated Python extension object owns one native derived instance. | [`points.f90` result](wrapping-derived-types.md#complete-derived-type-example) |
| Native-owned storage | Native module state or another native owner controls allocation and release. | [`allocations.f90` module view](allocatable-arrays.md#complete-allocatable-example) |
| Borrowed view or child | Python refers to storage owned by a module or containing wrapper. | [`points.f90` nested child](wrapping-derived-types.md#complete-derived-type-example) |
| Snapshot copy | Python receives detached current pointer state. | [`pointers.f90` result](pointer-arguments.md#complete-pointer-example) |
| Call-local association | Native code may refer to Python storage only during one wrapped call. | [`pointers.f90` input](pointer-arguments.md#complete-pointer-example) |

Those linked pages contain the full source, build commands, and asserted
results. The examples are not repeated here so ownership differences remain
attached to one canonical source listing.

## Core Invariants

1. Exactly one owner destroys each owned native allocation.
2. Python-owned copies and pointer snapshots are independent of later native mutation.
3. Caller-owned arrays are never freed by x2py.
4. A borrowed child or component view retains its generated wrapper owner.
5. Owner retention does not protect a view from explicit native reallocation or deallocation.
6. A pointer declaration never proves ownership of its target.
7. Missing owner, lifetime, release, shape, dtype, mutability, nullability, or aliasing facts block generation.

## Destruction Responsibilities

| Value | Release responsibility |
| --- | --- |
| scalar, string, copy-return array, pointer snapshot | Python, NumPy, or its generated base capsule |
| caller-supplied NumPy array | Python caller |
| wrapper-owned derived instance | generated wrapper deallocator and native finalization |
| borrowed nested component | containing wrapper owner |
| borrowed allocatable component view | containing native instance |
| borrowed allocatable module view | native module allocation routines |
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

- ordinary caller-owned arrays mutate in place;
- Python strings use replacement because `str` is immutable;
- allocatable inout arrays use replacement because native allocation identity
  may change;
- array/function results use copy-return;
- supported pointer results use snapshot-copy; and
- borrowed allocatable views share native storage until native invalidation.

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
and `Destruction(...)` metadata. Follow
[Editing Semantic `.pyi` Contracts](editing-semantic-pyi-contracts.md#ownership-lifetime-and-deallocation)
and the
[semantic format reference](../reference/semantic-pyi-format.md#ownership-transfer-and-destruction-policies).
Metadata can select an implemented policy; it cannot invent a backend path.

## Evidence And Troubleshooting

The same array concept under native-owned, wrapper-owned, and Python-owned
lifetimes is exercised by
[`test_ownership_contracts.py`](../../tests/wrapper/fortran/edit_pyi_contracts/test_ownership_contracts.py).
Exactly-once wrapper finalization is exercised by
[`test_borrowed_finalizers.py`](../../tests/wrapper/fortran/derived_types/test_borrowed_finalizers.py).

Treat use-after-deallocation risk as an application lifetime bug, not a signal
to guess ownership. Copy before native reallocation, and use
[Runtime Issues](../troubleshooting/runtime-issues.md) for reproducible lifetime
or cleanup symptoms.
