---
title: Pointers
audience: advanced users
prerequisites: arrays, memory management
related: allocatables.md, memory-management.md, ../reference/semantic-pyi-format.md
status: maintained
publication: reviewed
---

# Pointers

A Fortran pointer does not identify the target owner. Scalar pointers cross
procedure boundaries as ordinary nullable Python values plus bridge descriptor
metadata. Pointer arrays use `Pointer[T[...]]`, which is a Python handle to
native pointer association state, not a NumPy array.

## Array Handles

`Pointer[T[...]]` is the active pointer-array spelling in semantic `.pyi`
contracts:

```python
from x2py.contracts import Float64, Int32, Pointer

values: Pointer[Float64[:]]

def reassociate(values: Pointer[Float64[:]], target: Pointer[Float64[:]]) -> None: ...
def scale(values: Float64[:], factor: Int32) -> None: ...
```

The handle owns association state. An unassociated descriptor is still a
present handle: `p.associated is False`, `p.shape is None`, and
`p.to_numpy() is None`. `| None` means the handle object itself may be absent
for an optional native dummy, making native `present(values)` false:

```python
def maybe_use(values: Pointer[Float64[:]] | None = ...) -> None: ...
```

That spelling is valid only for optional callable arguments. Do not use
`Pointer[T[...]] | None` for module variables, derived-type fields, or function
results; those surfaces return a present handle, and unassociated state is
represented inside that handle.

Passing a handle to `Pointer[T[...]]` passes the native pointer descriptor.
Passing an associated handle to a normal `T[...]` parameter uses ordinary
Fortran array-actual semantics by handing off the handle's native array data
facet. It is not an implicit call to `.to_numpy()`. A normal `T[...]` parameter
rejects an unassociated pointer handle because there is no valid array actual
to pass; an associated zero-length target remains valid. The pointer/shape
handoff accepts only targets proved contiguous. A noncontiguous target is
rejected until descriptor-backed stride handoff is selected; x2py never treats
such a target as contiguous.

Plain NumPy arrays are accepted by normal `T[...]` array parameters. They are
rejected for `Pointer[T[...]]` descriptor parameters because a NumPy array does
not carry a native pointer descriptor.

`p.to_numpy()` is the explicit extraction operation. It returns `None` when the
handle is unassociated. When descriptor extraction is supported, it returns the
current target view and may expose strided targets. It never creates an
automatic detached snapshot or copy. If no supported live-view mechanism can
expose the current target, policy completion or wrapper planning fails explicitly;
x2py does not guess compiler-specific descriptor layout or fall back to a copy.

Any NumPy view returned by `p.to_numpy()` is tied to the pointer target at the
time of extraction. After native code nullifies, reassociates, deallocates, or
otherwise changes that target, discard older views and call `p.to_numpy()`
again. Accessing a stale view is unsupported and may crash. Users who need
independent storage must call `.copy()` before the target-changing operation.
Each fresh extraction inspects the current descriptor and starts at the
target's current native lower bounds rather than assuming a fixed Fortran lower
bound.

`p.nullify()` is the default pointer descriptor operation. `allocate(shape)`,
`deallocate()`, and `resize(shape)` are exposed only when completed pointer
policy explicitly allows those operations. A pointer handle does not imply
target ownership.

## Scalar Pointer Projections

Supported scalar pointer dummies use ordinary nullable Python values. The
semantic `.pyi` uses `Pointer(...)` inside `@native_call` to construct or read
the native pointer descriptor without exposing a Python pointer handle.

For example:

```fortran
real(8), target :: target_scale

subroutine update_pointer(scale)
  real(8), pointer, intent(inout) :: scale

  if (associated(scale)) then
    scale = scale + 1.0_8
  else
    scale => target_scale
  end if
end subroutine update_pointer

function maybe_pointer(enabled) result(scale)
  integer(4), intent(in) :: enabled
  real(8), pointer :: scale

  nullify(scale)
  if (enabled /= 0) scale => target_scale
end function maybe_pointer
```

The corresponding semantic contract keeps scalar pointer values nullable and
uses `Pointer(...)` only for native descriptor projection:

```python
from x2py.contracts import Addr, Arg, Float64, Int32, Pointer, Return, Returns, native_call

@native_call([Pointer(Arg(0))])
def update_pointer(
    scale: Float64 | None,
) -> Returns["scale", Float64] | None: ...

@native_call([Addr(Arg(0))], result=Pointer(Return(0)))
def maybe_pointer(enabled: Int32) -> Float64 | None: ...
```

Passing `None` creates a present but unassociated call-local descriptor.
Omitting a defaulted scalar descriptor argument creates native optional absence,
so `present(scale)` is false. Passing a value creates a present associated
call-local descriptor. An unassociated function result or projected output
becomes `None`. Ordinary scalar projection rules remain unchanged: `intent(out)`
uses `Pointer(Return("name", j))`, and `intent(inout)` uses `Pointer(Arg(i))`
plus a matching `Returns["name", T] | None` readback. Scalar pointer values do
not expose a handle API.

Use a default only when the native scalar dummy is optional:

```python
@native_call([Pointer(Arg(0))])
def update_pointer(scale: Float64 | None = ...) -> None: ...
```

This scalar rule is separate from array pointer handles. Array arguments use
`Pointer[T[...]] | None` only for an optional absent handle; unassociated array
state stays inside a present handle.

## Complete Pointer Example

Create `pointers.f90`:

```fortran
module pointers_api
  implicit none
  real(8), target :: storage(3) = [1.0_8, 2.0_8, 3.0_8]
  real(8), pointer :: values(:) => null()
contains
  subroutine associate_values()
    values => storage
  end subroutine associate_values

  real(8) function sum_array(actual) result(total)
    real(8), intent(in) :: actual(:)
    total = sum(actual)
  end function sum_array

  real(8) function sum_pointer(actual) result(total)
    real(8), pointer, intent(in) :: actual(:)

    if (associated(actual)) then
      total = sum(actual)
    else
      total = -1.0_8
    end if
  end function sum_pointer
end module pointers_api
```

The generated semantic contract distinguishes the module descriptor, an
ordinary array parameter, and a pointer-descriptor parameter:

```python
from x2py.contracts import (
    Aliased,
    Annotated,
    Destruction,
    Float64,
    Ownership,
    Pointer,
    PointerAssociation,
    Transfer,
)

storage: Annotated[Float64[3], Aliased]
values: Annotated[Pointer[Float64[:]], PointerAssociation("runtime")]

def associate_values() -> None: ...
def sum_array(actual: Float64[::]) -> Float64: ...
def sum_pointer(
    actual: Annotated[
        Pointer[Float64[:]],
        PointerAssociation("runtime"),
        Ownership("caller"),
        Transfer("call_local"),
        Destruction("none"),
    ]
) -> Float64: ...
```

Build it:

```bash
python3 -m x2py pointers.f90 --out-dir build/pointers
```

Then verify descriptor state, descriptor passing, and normal array-actual
handoff from the same handle:

```python
import sys

import numpy as np

sys.path.insert(0, "build/pointers")
import pointers

api = pointers.pointers_api
handle = api.values

assert handle.associated is False
assert handle.shape is None
assert api.sum_pointer(handle) == np.float64(-1.0)

api.associate_values()
assert handle.associated is True
assert handle.shape == (3,)
assert api.sum_pointer(handle) == np.float64(6.0)
assert api.sum_array(handle) == np.float64(6.0)

handle.nullify()
assert handle.associated is False
```

The ordinary `sum_array` call uses the handle's valid contiguous array actual;
it does not call `to_numpy()`. The descriptor-typed `sum_pointer` call requires
the pointer handle and can observe unassociated state. Add explicit pointer
policy when public NumPy extraction or ownership-changing operations are
required.

## Call Compatibility

A normal `T[...]` array parameter may accept a plain NumPy array or an
associated `Pointer[T[...]]` handle. The NumPy path passes caller-owned array
storage. The handle path validates pointer association, dtype, rank, shape,
layout, and mutability, then passes the handle's native array actual to the
normal native array dummy. The two paths share validation policy but remain
separate implementation methods.

If the user writes `api.scale(p.to_numpy())`, that is an explicit ndarray path.
The returned value from `to_numpy()` follows ordinary ndarray validation,
including rejection of `None` and read-only arrays when writable native storage
is required.

## Pointer Results

An associated pointer scalar result becomes a copied Python value. An
unassociated scalar result becomes `None`.

Pointer-array handle results remain blocked until x2py has stable owner storage,
target lifetime, descriptor extraction, and generated destroy behavior for the
returned handle. The wrapper does not silently fall back to a detached NumPy
copy for `Pointer[T[...]]` results.

## Pointer Fields And Module Variables

Pointer-backed array fields and module variables expose `Pointer[T[...]]`
handles. Their runtime Python class is `PointerArray`. A scalar pointer to a
derived object instead returns its generated live wrapper or `None`.
The containing object or module does not automatically own the pointer target.
Derived-field handles keep the parent wrapper alive for descriptor access, but
that retention is not target ownership. Plain `Pointer[T[...]]` has a default
conservative handle policy for association inspection and legal descriptor
operations. Generated field operations address the component through its parent
wrapper, and generated module operations address the native module variable.
Neither path invents target ownership or enables ownership-changing operations
that completed pointer policy did not allow.

An associated scalar derived module pointer can be passed to an ordinary,
target, input-only pointer, or value dummy through its current target. For a
reassociable pointer dummy, x2py uses a typed local pointer holder and restores
the final association—associated, reassociated, allocated, disassociated, or
deallocated—to the module pointer exactly once. A wrapper-owned pointer result
uses the same persistent holder component directly. The holder owns its
association variable, not an unknown target, and its destructor never
deallocates native-owned target storage. Nullification or reassociation makes an
older payload proxy stale, and later field access raises `ReferenceError`.

The later Wrapping Derived Types guide gives the canonical “Scalar Actuals And
Native Dummies” matrix, including the `INTENT(IN)` exception for nonpointer
actuals, empty-state behavior, module transactions, and multi-argument cleanup.

## Unsupported Forms

- pointer array `intent(out)` and `intent(inout)` reassociation without a
  completed descriptor policy;
- pointer `allocate()`, `deallocate()`, or `resize()` without explicit policy;
- unknown target owners or release responsibility;
- persistent associations to Python storage after return; and
- stale-view invalidation after target reassociation, nullification, or
  deallocation; and
- scalar-derived pointer targets whose lifetime or release responsibility is
  neither native nor tied to a retained known owner.

Semantic `.pyi` metadata can record these policy facts, but metadata does not
implement a missing runtime path.

## Evidence And Troubleshooting

Scalar pointer inputs, outputs, inout readback, nullable results, array pointer
handles, descriptor views, normal array-actual handoff, and dtype rejection are exercised by
[`test_pointers.py`](../../../tests/wrapper/fortran/derived_types/test_pointers.py).
Scalar derived module-pointer state, reassociation writeback, wrapper pointer
holders, stale proxy rejection, and multi-argument cleanup are exercised by
[`test_scalar_derived_actual_dummy_matrix.py`](../../../tests/wrapper/fortran/derived_types/test_scalar_derived_actual_dummy_matrix.py).
The scalar `out` and `inout` parity cases are exercised by
[`test_allocatable_views.py`](../../../tests/wrapper/fortran/module_state/test_allocatable_views.py).

If wrapper planning rejects a pointer, do not replace the diagnostic with guessed
ownership metadata. Detached pointer result behavior is expressible only when shape,
nullability, target owner, lifetime, and release facts are complete. Memory
Management and the semantic `.pyi` ownership reference expand those decisions
later.
