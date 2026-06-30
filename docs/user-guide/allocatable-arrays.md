---
title: Allocatable Arrays
audience: users, advanced users
prerequisites: arrays
related: arrays.md, pointer-arguments.md, memory-management.md
status: maintained
---

# Allocatable Arrays

Allocatable behavior depends on where the allocation lives. A top-level result
or output crosses as a Python-owned copy, an inout dummy crosses as a replacement,
and module or component storage can be a borrowed view owned by native state or
its containing wrapper object.

## Complete Allocatable Example

Create `allocations.f90`:

```fortran
module allocations_api
  implicit none
  real(8), allocatable, target :: shared_values(:)
contains
  function make_values(count) result(values)
    integer(4), intent(in) :: count
    real(8), allocatable :: values(:)
    integer(4) :: index

    if (count <= 0) return
    allocate(values(count))
    values = [(2.0_8 * index, index = 1, count)]
  end function make_values

  subroutine replace_values(values)
    real(8), allocatable, intent(inout) :: values(:)

    if (allocated(values)) deallocate(values)
    allocate(values(2))
    values = [10.0_8, 20.0_8]
  end subroutine replace_values

  subroutine allocate_shared(count)
    integer(4), intent(in) :: count
    integer(4) :: index

    if (allocated(shared_values)) deallocate(shared_values)
    allocate(shared_values(count))
    shared_values = [(1.0_8 * index, index = 1, count)]
  end subroutine allocate_shared

  subroutine release_shared()
    if (allocated(shared_values)) deallocate(shared_values)
  end subroutine release_shared

  real(8) function shared_sum() result(total)
    total = sum(shared_values)
  end function shared_sum
end module allocations_api
```

Build it:

```bash
python3 -m x2py allocations.f90 \
  --wrap \
  --out-dir build/allocations \
  --json
```

Then exercise copy, replacement, and borrowed-view behavior:

```python
import sys

import numpy as np

sys.path.insert(0, "build/allocations")
import allocations

api = allocations.allocations_api

copy = api.make_values(np.int32(3))
np.testing.assert_array_equal(copy, np.array([2.0, 4.0, 6.0], dtype=np.float64))
assert api.make_values(np.int32(0)) is None

original = np.array([1.0, 2.0], dtype=np.float64)
replacement = api.replace_values(original)
np.testing.assert_array_equal(original, np.array([1.0, 2.0], dtype=np.float64))
np.testing.assert_array_equal(replacement, np.array([10.0, 20.0], dtype=np.float64))

api.allocate_shared(np.int32(3))
view = api.shared_values
view[0] = np.float64(10.0)
assert api.shared_sum() == np.float64(15.0)
```

Do not access `view` after `api.release_shared()`; native deallocation makes
the previous borrowed view stale.

## Output And Function Results

Allocated top-level results and hidden allocatable outputs are copied into new
Python-owned NumPy arrays. The native temporary is released after the copy.
Unallocated storage becomes `None`, while allocated zero-sized storage remains
a zero-sized array.

Changing the returned NumPy array does not mutate later native results or module
state.

## Inout Replacement

An allocatable `intent(inout)` argument accepts `None` for initially
unallocated storage or an exact matching NumPy array. A supplied array is
copied into temporary native allocatable storage and is not mutated. Python
receives the final native allocation as a new array or `None`.

This is replacement behavior, not ordinary in-place array mutation. Assign the
return value:

```python
values = api.replace_values(values)
```

The source for this call is already shown in the complete example above.

## Module And Component Views

A target-backed allocatable module array is native-owned. Reading its Python
attribute returns a borrowed NumPy view or `None`. Mutation reaches native
module storage; deleting the NumPy view does not deallocate that storage.

A supported allocatable component belongs to its containing native derived-type
instance. Its NumPy view uses the generated wrapper object as `view.base`, which
keeps the owner alive. Assigning a replacement array directly to such a field
is rejected when native reallocation must go through an explicit method.

Neither owner model can invalidate an already-created NumPy object safely after
native reallocation. Copy before any operation that may reallocate or
deallocate:

```python
independent = view.copy()
```

## Limitations

- Allocatable scalar derived-type dummy replacement is blocked.
- Character allocatable arrays and mutable deferred-length character storage
  are blocked.
- Borrowed views require a proved native or wrapper owner and supported target
  storage.
- An edited `.pyi` cannot relabel a native-owned allocation as Python-owned
  without choosing an implemented copy-return path.

## Evidence And Troubleshooting

Results, module views, component views, `None`, and owner retention are exercised
by
[`test_allocatable_views.py`](../../tests/wrapper/fortran/module_state/test_allocatable_views.py).
Replacement behavior and invalid dtype/rank calls are exercised by
[`test_allocatable_replacement.py`](../../tests/wrapper/fortran/module_state/test_allocatable_replacement.py).

Use [Memory Management](memory-management.md) before retaining a view and
[Runtime Issues](../troubleshooting/runtime-issues.md) for dtype, rank, or stale
storage symptoms.
