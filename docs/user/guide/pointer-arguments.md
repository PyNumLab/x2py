---
title: Pointer Arguments
audience: advanced users
prerequisites: arrays, memory management
related: allocatable-arrays.md, memory-management.md, ../reference/semantic-pyi-format.md
status: maintained
---

# Pointer Arguments

A Fortran pointer does not identify the target owner. x2py therefore supports a
conservative subset: call-local input association and detached snapshot results.
General borrowed pointer views and pointer reassociation remain blocked.

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

Then verify call-local input and snapshot output:

```python
import sys

import numpy as np

sys.path.insert(0, "build/pointers")
import pointers

api = pointers.pointers_api
values = np.array([1.0, 2.0, 3.0], dtype=np.float64)
assert api.sum_pointer(values) == np.float64(6.0)

snapshot = api.select_values(values, np.int32(1))
assert api.select_values(values, np.int32(0)) is None
snapshot[0] = np.float64(99.0)
np.testing.assert_array_equal(values, np.array([1.0, 2.0, 3.0], dtype=np.float64))
```

## Call-Local Inputs

A supported pointer `intent(in)` scalar or array may associate with converted
Python storage only while the wrapped call executes. Native code must not save
the association for later use. Python remains the owner of the input array.

The wrapper still validates exact dtype, rank, shape, layout, alignment, and
read-only requirements. Pointer syntax does not permit an implicit conversion
or unsafe array view.

## Snapshot Results

An associated pointer scalar result becomes a copied Python value. An associated
pointer array result becomes a Python-owned NumPy snapshot. An unassociated
result becomes `None`.

Snapshots do not alias the native target or one another. Mutation of a snapshot
does not reach the original input, and deleting the input does not invalidate
the snapshot.

Snapshot generation requires known association state, dtype, shape,
contiguity, nullability, target owner, and deallocation obligations. Missing
facts produce a readiness blocker.

## Pointer Fields And Module Variables

Pointer-backed fields and module variables use snapshot-or-block policy. The
containing object or module does not automatically own the pointer target.
Where a safe snapshot cannot be proved, the declaration is blocked instead of
exposing a borrowed view.

## Unsupported Forms

- pointer `intent(out)` and `intent(inout)` reassociation;
- general zero-copy borrowed pointer views;
- unknown target owners or release responsibility;
- persistent associations to Python storage after return; and
- stale-view invalidation after target reassociation or deallocation.

Semantic `.pyi` metadata can record these policy facts, but metadata does not
implement a missing runtime path.

## Evidence And Troubleshooting

Scalar and array pointer inputs, nullable results, independent snapshots, and
dtype rejection are exercised by
[`test_pointers.py`](../../../tests/wrapper/fortran/derived_types/test_pointers.py).

If readiness blocks a pointer, do not replace the diagnostic with guessed
ownership metadata. Snapshot behavior is expressible only when shape,
nullability, target owner, lifetime, and release facts are complete. Memory
Management and the semantic `.pyi` ownership reference expand those decisions
later.
