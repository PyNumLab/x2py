---
title: Pointers
audience: advanced users
prerequisites: arrays, memory management
related: allocatables.md, memory-management.md, ../reference/semantic-pyi-format.md
status: maintained
---

# Pointers

A Fortran pointer does not identify the target owner. x2py therefore supports a
conservative subset: call-local input association and detached copied results.
General borrowed pointer views and pointer reassociation remain blocked.

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

The corresponding semantic contract is:

```python
from x2py.contracts import Addr, Arg, Float64, Int32, Pointer, Return, Returns, native_call

@native_call([Pointer(Arg(0))])
def update_pointer(
    scale: Float64 | None,
) -> Returns["scale", Float64] | None: ...

@native_call([Addr(Arg(0))], result=Pointer(Return(0)))
def maybe_pointer(enabled: Int32) -> Float64 | None: ...
```

Passing `None` creates an unassociated call-local descriptor. An unassociated
function result or projected output becomes `None`. Ordinary scalar projection
rules remain unchanged: `intent(out)` uses `Pointer(Return("name", j))`, and
`intent(inout)` uses `Pointer(Arg(i))` plus a matching
`Returns["name", T] | None` readback. Pointer arrays and persistent borrowed
targets still require separate ownership and lifetime policy.

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

Then verify call-local input and detached output:

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

## Call-Local Inputs

A supported pointer `intent(in)` scalar or array may associate with converted
Python storage only while the wrapped call executes. Native code must not save
the association for later use. Python remains the owner of the input array.

The wrapper still validates exact dtype, rank, shape, layout, alignment, and
read-only requirements. Pointer syntax does not permit an implicit conversion
or unsafe array view.

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

Pointer-backed fields and module variables use detached-copy-or-block policy. The
containing object or module does not automatically own the pointer target.
Where a safe detached copy cannot be proved, the declaration is blocked instead of
exposing a borrowed view.

## Unsupported Forms

- pointer array `intent(out)` and `intent(inout)` reassociation;
- general zero-copy borrowed pointer views;
- unknown target owners or release responsibility;
- persistent associations to Python storage after return; and
- stale-view invalidation after target reassociation or deallocation.

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
