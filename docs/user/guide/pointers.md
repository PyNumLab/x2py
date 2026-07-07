---
title: Pointers
audience: advanced users
prerequisites: arrays, memory management
related: allocatables.md, memory-management.md, ../reference/semantic-pyi-format.md
status: maintained
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
to pass; an associated zero-length target remains valid.

Plain NumPy arrays are accepted by normal `T[...]` array parameters. They are
rejected for `Pointer[T[...]]` descriptor parameters because a NumPy array does
not carry a native pointer descriptor.

`p.to_numpy()` is the explicit extraction operation. It returns `None` when the
handle is unassociated. When descriptor extraction is supported, it returns the
current target view and may expose strided targets. If descriptor extraction is
unavailable, policy must choose a contiguous-only path, an explicit copy
fallback, or a readiness diagnostic; x2py must not guess compiler-specific
descriptor layout.

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
contains
  real(8) function sum_pointer(values) result(total)
    real(8), pointer, intent(in) :: values(:)
    total = sum(values)
  end function sum_pointer

  function select_values(values, enabled) result(selected)
    real(8), target, intent(in) :: values(:)
    integer(4), intent(in) :: enabled
    real(8), pointer :: selected(:)

    nullify(selected)
    if (enabled /= 0) selected => values
  end function select_values
end module pointers_api
```

Build it:

```bash
python3 -m x2py pointers.f90 --out-dir build/pointers
```

Then verify call-local scalar-style input and detached output behavior:

```python
import sys

import numpy as np

sys.path.insert(0, "build/pointers")
import pointers

api = pointers.pointers_api
values = np.array([1.0, 2.0, 3.0], dtype=np.float64)
assert api.sum_pointer(values) == np.float64(6.0)

selected = api.select_values(values, np.int32(1))
assert api.select_values(values, np.int32(0)) is None
selected[0] = np.float64(99.0)
np.testing.assert_array_equal(values, np.array([1.0, 2.0, 3.0], dtype=np.float64))
```

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

## Detached Pointer Results

An associated pointer scalar result becomes a copied Python value. An associated
pointer array result becomes a detached Python-owned NumPy array. An unassociated
result becomes `None`.

Detached pointer results do not alias the native target or one another. Mutation
of the returned array does not reach the original input, and deleting the input
does not invalidate the returned array.

This detached-copy path requires known association state, dtype, shape,
contiguity, nullability, target owner, and deallocation obligations. Missing
facts produce a readiness blocker.

## Pointer Fields And Module Variables

Pointer-backed fields and module variables expose `Pointer[T[...]]` handles.
The containing object or module does not automatically own the pointer target.
Derived-field handles keep the parent wrapper alive for descriptor access, but
that retention is not target ownership. Where target lifetime, descriptor
extraction, or release policy is incomplete, wrapper readiness blocks instead
of exposing a guessed borrowed view.

## Unsupported Forms

- pointer array `intent(out)` and `intent(inout)` reassociation without a
  completed descriptor policy;
- pointer `allocate()`, `deallocate()`, or `resize()` without explicit policy;
- unknown target owners or release responsibility;
- persistent associations to Python storage after return; and
- stale-view invalidation after target reassociation, nullification, or
  deallocation.

Semantic `.pyi` metadata can record these policy facts, but metadata does not
implement a missing runtime path.

## Evidence And Troubleshooting

Scalar pointer inputs, outputs, inout readback, nullable results, array pointer
inputs, independent detached copies, and dtype rejection are exercised by
[`test_pointers.py`](../../../tests/wrapper/fortran/derived_types/test_pointers.py).
The scalar `out` and `inout` parity cases are exercised by
[`test_allocatable_views.py`](../../../tests/wrapper/fortran/module_state/test_allocatable_views.py).

If readiness blocks a pointer, do not replace the diagnostic with guessed
ownership metadata. Detached pointer result behavior is expressible only when shape,
nullability, target owner, lifetime, and release facts are complete. Memory
Management and the semantic `.pyi` ownership reference expand those decisions
later.
