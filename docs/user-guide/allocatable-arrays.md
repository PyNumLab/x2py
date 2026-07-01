---
title: Allocatable Arrays
audience: users, advanced users
prerequisites: arrays
related: arrays.md, pointer-arguments.md, memory-management.md
status: maintained
---

# Allocatable Arrays

Allocatable behavior depends on which side owns the allocation. The Python
value may be a copy, a replacement, or a borrowed view into storage owned
somewhere else.

| Case | Python sees | Owner and lifetime |
| --- | --- | --- |
| Function result or hidden allocatable output | new NumPy array, or `None` when unallocated | Python owns the returned copy; the native temporary is released |
| Allocatable `intent(inout)` dummy | replacement NumPy array or `None` | Python owns the returned replacement; the original argument is unchanged |
| Target-backed allocatable module variable | borrowed NumPy view or `None` | the Fortran module owns allocation and release |
| Allocatable derived-type field | borrowed NumPy view or `None` | the containing generated wrapper owns the native instance |

`Allocatable` is the dynamic-storage fact shared by all rows. It does not by
itself choose copy, replacement, or borrowed-view behavior. The declaration
context and completed ownership policy choose that behavior.

A borrowed view is a NumPy array that points at storage Python does not own.
Mutating the view mutates the owner. Deallocating or reallocating the owner can
make existing views stale, so copy the view when Python needs an independent
lifetime.

## Complete Allocatable Example

Create `allocations.f90`:

```fortran
module storage
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
end module storage
```

Inspecting `allocations.f90` prints the copy, replacement, and borrowed-view
contracts:

```python
shared_values: Annotated[Float64[:], Allocatable, FortranTarget] | None

@native_call([Ref(Arg(0))])
def make_values(
    count: Const(Int32)
) -> Annotated[Float64[:], Allocatable]: ...

@native_call([Arg(0)])
def replace_values(
    values: Annotated[Float64[:], Allocatable]
) -> Returns["values", Annotated[Float64[:], Allocatable], Optional]: ...

@native_call([Ref(Arg(0))])
def allocate_shared(
    count: Const(Int32)
) -> None: ...

def release_shared() -> None: ...

def shared_sum() -> Float64: ...
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

api = allocations.storage

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

Allocated top-level results and hidden allocatable outputs use copy-return:
x2py copies the native allocation into a new Python-owned NumPy array and then
releases the native temporary. Unallocated storage becomes `None`, while
allocated zero-sized storage remains a zero-sized array.

Changing the returned NumPy array does not mutate later native results or module
state.

## Inout Replacement

An allocatable `intent(inout)` argument accepts `None` or an exact matching
NumPy array. x2py copies the supplied value into temporary native allocatable
storage. The Python argument remains Python-owned and is not mutated.

After the call, x2py copies the final native allocation into a new Python-owned
return value, or returns `None` if native storage is unallocated. This is
replacement behavior, not ordinary in-place array mutation. Assign the return
value:

```python
values = api.replace_values(values)
```

The source for this call is already shown in the complete example above.

## Module And Component Views

A target-backed allocatable module array is native-owned. The module's
allocation routines create and release the storage. Reading the Python
attribute returns a borrowed NumPy view or `None`. Mutating the view reaches
native module storage; deleting the view does not deallocate that storage.
The generated `.pyi` marks the module variable with `FortranTarget`, matching
the Fortran `target` attribute needed to take the native address. `FortranTarget`
is not an ownership mode and does not by itself mean "borrowed view".

A supported allocatable component belongs to its containing native derived-type
instance. The generated wrapper owns that native instance. Its NumPy view uses
the wrapper object as `view.base`, which keeps the owner alive. Assigning a
replacement array directly to such a field is rejected when native reallocation
must go through an explicit method.

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
