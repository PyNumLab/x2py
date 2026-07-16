---
title: Allocatables
audience: users, advanced users
prerequisites: arrays
related: arrays.md, pointers.md, memory-management.md
status: maintained
---

# Allocatables

Allocatable behavior depends on whether the contract describes a scalar
descriptor projection or an array descriptor handle. Scalar allocatables cross
procedure boundaries as ordinary nullable Python values. Array allocatables use
`Allocatable[T[...]]`, which is a Python handle to a native allocatable
descriptor, not a NumPy array.

| Case | Python sees | Owner and lifetime |
| --- | --- | --- |
| Scalar allocatable projection | `T | None` | a call-local native descriptor is created or read back by the bridge |
| Allocatable descriptor argument | `Allocatable[T[...]]` handle | the handle passes the native allocatable descriptor |
| Module allocatable array | `Allocatable[T[...]]` handle | the Fortran module owns allocation and release |
| Derived allocatable field | `Allocatable[T[...]]` handle | the containing generated wrapper owns the native instance |
| Owned allocatable result | `Allocatable[T[...]]` handle | x2py-owned descriptor storage releases the native allocation with the handle |

`Allocatable` is the dynamic-storage fact shared by all rows. It does not by
itself choose copy, replacement, borrowed-view, or owned-handle behavior. The
declaration context and completed ownership policy choose that behavior before
wrapper lowering.

At runtime, every allocatable array handle described below is an
`AllocatableArray`. Scalar allocatables never produce an `AllocatableArray`;
they remain ordinary `T | None` values at the Python boundary.

## Array Handles

`Allocatable[T[...]]` is the active allocatable-array spelling in semantic
`.pyi` contracts:

```python
from x2py.contracts import Allocatable, Float64, Int32

values: Allocatable[Float64[:]]

def resize(values: Allocatable[Float64[:]], n: Int32) -> None: ...
def scale(values: Float64[:]) -> None: ...
```

The handle owns the allocation state, so an unallocated descriptor is still a
present handle: `h.allocated is False`, `h.shape is None`, and
`h.to_numpy() is None`. `| None` means the handle object itself may be absent
for an optional native dummy, making native `present(values)` false:

```python
def maybe_resize(values: Allocatable[Float64[:]] | None = ...) -> None: ...
```

That spelling is valid only for optional callable arguments. Do not use
`Allocatable[T[...]] | None` for module variables, derived-type fields, or
function results; those surfaces return a present handle. Module variables,
fields, allocatable output dummies, and handles changed by later operations may
be unallocated. A native allocatable function result must be allocated when the
function returns; returning it unallocated is nonconforming Fortran and x2py
does not define a fallback for it.

Passing a handle to `Allocatable[T[...]]` passes the native descriptor. Passing
the same allocated handle to a normal `T[...]` argument uses ordinary Fortran
array-actual semantics by handing off the handle's native array data facet. It
is not an implicit call to `.to_numpy()`. A normal `T[...]` argument rejects an
unallocated handle because there is no valid array actual to pass; an allocated
zero-length array remains valid.

Plain NumPy arrays are accepted by normal `T[...]` array parameters. They are
rejected for `Allocatable[T[...]]` descriptor parameters because a NumPy array
does not carry a native allocatable descriptor.

`h.to_numpy()` is the explicit extraction operation. It returns `None` when the
handle is unallocated. Otherwise, it returns a live mutable NumPy view of the
current native allocation. It never creates an automatic detached snapshot or
copy. Users who need independent storage must explicitly call `.copy()` on the
returned array.

A borrowed view is a NumPy array that points at storage Python does not own.
Mutating the view mutates the owner. Deallocating or reallocating the owner can
make an existing view stale. Accessing a stale view is unsupported and may
crash the process; discard it and call `to_numpy()` again after the native state
changes. Each fresh extraction inspects the current descriptor and starts at
the current native lower bounds. Changing lower bounds during native
reallocation must not offset the first element exposed to NumPy.

An allocatable array returned by a function or hidden output is different from
a borrowed module or field handle. x2py transfers the result into persistent
descriptor storage owned by the returned handle. The handle remains
usable after the native call returns, and `close()` or finalization releases the
native allocation. A NumPy view extracted from that handle retains the handle;
as with every live view, explicitly closing or resizing the handle makes older
views stale.

## Scalar Allocatable Projections

Scalar allocatables cross a procedure boundary as ordinary nullable Python
values. The semantic `.pyi` keeps the Python annotation as `T | None` and uses
`Allocatable(...)` inside `@native_call` to describe native descriptor
construction and readback.

For example:

```fortran
function maybe_scale(enabled) result(scale)
  integer(4), intent(in) :: enabled
  real(8), allocatable :: scale

  if (enabled /= 0) then
    allocate(scale)
    scale = 2.5_8
  end if
end function maybe_scale

subroutine update_scale(scale)
  real(8), allocatable, intent(inout) :: scale

  if (allocated(scale)) then
    scale = scale + 1.0_8
  else
    allocate(scale)
    scale = 1.0_8
  end if
end subroutine update_scale
```

The corresponding semantic contract is:

```python
from x2py.contracts import Addr, Allocatable, Arg, Float64, Int32, Return, Returns, native_call

@native_call([Addr(Arg(0))], result=Allocatable(Return(0)))
def maybe_scale(enabled: Int32) -> Float64 | None: ...

@native_call([Allocatable(Arg(0))])
def update_scale(
    scale: Float64 | None,
) -> Returns["scale", Float64] | None: ...
```

Passing `None` creates a present but unallocated call-local descriptor. Omitting
a defaulted scalar descriptor argument creates native optional absence, so
`present(scale)` is false. Passing a value creates a present allocated
call-local descriptor. A projected output becomes `None` when its descriptor is
unallocated. An allocatable function result must instead be allocated and
defined when returned; an unallocated result is nonconforming native Fortran,
not a nullable x2py value. Ordinary scalar projection rules still apply:
`intent(out)` uses `Allocatable(Return("name", j))`, while `intent(inout)` uses
`Allocatable(Arg(i))` plus a matching `Returns["name", T] | None` readback. The
singular `result=Allocatable(Return(j))` mapping describes the native function
result and places it among any other Python results.

Use a default only when the native scalar dummy is optional:

```python
@native_call([Allocatable(Arg(0))])
def update_scale(scale: Float64 | None = ...) -> None: ...
```

This scalar rule is separate from array allocatable handles. Array arguments use
`Allocatable[T[...]] | None` only for an optional absent handle; unallocated array
state stays inside a present handle.

## Complete Allocatable Example

Create `allocations.f90`:

```fortran
module storage
  implicit none
  real(8), allocatable, target :: shared_values(:)
  real(8), allocatable :: plain_values(:)
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

  subroutine allocate_plain(count)
    integer(4), intent(in) :: count
    integer(4) :: index

    if (allocated(plain_values)) deallocate(plain_values)
    allocate(plain_values(count))
    plain_values = [(3.0_8 * index, index = 1, count)]
  end subroutine allocate_plain

  subroutine release_shared()
    if (allocated(shared_values)) deallocate(shared_values)
  end subroutine release_shared

  subroutine scale_plain(scale)
    real(8), intent(in) :: scale
    plain_values = scale * plain_values
  end subroutine scale_plain

  subroutine release_plain()
    if (allocated(plain_values)) deallocate(plain_values)
  end subroutine release_plain

  real(8) function shared_sum() result(total)
    total = sum(shared_values)
  end function shared_sum
end module storage
```

Inspecting `allocations.f90` prints allocatable array handles for module
storage, descriptor results, and descriptor arguments. `Aliased` remains a
language-neutral fact that native storage may be externally aliased or
addressed. It does not change `to_numpy()` extraction semantics:

```python
from x2py.contracts import Addr, Aliased, Allocatable, Annotated, Arg, Float64, Int32, Returns, native_call

shared_values: Annotated[Allocatable[Float64[:]], Aliased]
plain_values: Allocatable[Float64[:]]

@native_call([Addr(Arg(0))])
def make_values(
    count: Int32
) -> Allocatable[Float64[:]]: ...

def replace_values(
    values: Allocatable[Float64[:]]
) -> Returns["values", Allocatable[Float64[:]]]: ...

@native_call([Addr(Arg(0))])
def allocate_shared(
    count: Int32
) -> None: ...

@native_call([Addr(Arg(0))])
def allocate_plain(
    count: Int32
) -> None: ...

def release_shared() -> None: ...

def scale_plain(
    scale: Float64
) -> None: ...

def release_plain() -> None: ...

def shared_sum() -> Float64: ...
```

`plain_values` and `shared_values` have the same extraction behavior: a fresh
`to_numpy()` call returns a live view of the current allocation or `None`.
`Aliased` remains present on `shared_values` because the native declaration
supplies the corresponding addressability fact. It does not change the
allocatable-array extraction mode.

Build it:

```bash
python3 -m x2py allocations.f90 --out-dir build/allocations
```

Then exercise owned-result, descriptor-argument, and module-handle behavior:

```python
import sys
import numpy as np

sys.path.insert(0, "build/allocations")
import allocations

api = allocations.storage

values = api.make_values(np.int32(3))
np.testing.assert_array_equal(values.to_numpy(), np.array([2.0, 4.0, 6.0], dtype=np.float64))
assert api.make_values(np.int32(0)).allocated is False

returned = api.replace_values(values)
assert returned is values
np.testing.assert_array_equal(values.to_numpy(), np.array([10.0, 20.0], dtype=np.float64))

api.allocate_shared(np.int32(3))
shared = api.shared_values
view = shared.to_numpy()
view[0] = np.float64(10.0)
assert api.shared_sum() == np.float64(15.0)

api.allocate_plain(np.int32(3))
plain_view = api.plain_values.to_numpy()
plain_copy = plain_view.copy()
plain_view[0] = np.float64(12.0)

api.scale_plain(np.float64(2.0))
np.testing.assert_array_equal(plain_copy, np.array([3.0, 6.0, 9.0], dtype=np.float64))
np.testing.assert_array_equal(
    api.plain_values.to_numpy(),
    np.array([24.0, 12.0, 18.0], dtype=np.float64),
)
```

Do not access `view` after `api.release_shared()`, or `plain_view` after
`api.release_plain()` or another reallocation. Native storage changes make the
previous views stale, and accessing a stale view is unsupported and may crash.

## Output And Function Results

Allocated top-level results and non-optional hidden allocatable outputs return
wrapper-owned `AllocatableArray` objects. The generated binding transfers the
result into persistent descriptor storage; the handle releases that storage on
`close()` or finalization. Unallocated storage is represented by a present
handle whose `allocated` property is false and whose `to_numpy()` result is
`None`. Optional allocatable outputs remain visible so the caller can omit them
and make native `present(...)` false.

A NumPy view returned by `to_numpy()` retains its handle owner. Changing that
view changes the handle's current allocation, but does not affect later,
independent result handles.

## Inout Replacement

An allocatable `intent(inout)` descriptor argument accepts an
`AllocatableArray`, not a plain NumPy array. A matching `Returns[...]`
projection records that the same caller handle is the Python result. Policy
completion marks that descriptor boundary read-write before lowering; generated
binding code does not manufacture a replacement ndarray or a second handle.

```python
assert api.replace_values(values) is values
```

The source for this call is already shown in the complete example above.

## Character Array Replacement

Allocatable character arrays use fixed-width NumPy bytes storage. Create
`character_allocatables.f90`:

```fortran
module character_names
  implicit none
contains
  function make_names() result(names)
    character(len=:), allocatable :: names(:)

    allocate(character(len=3) :: names(2))
    names = [character(len=3) :: "red", "sky"]
  end function make_names

  subroutine replace_names(names)
    character(len=:), allocatable, intent(inout) :: names(:)
    integer :: count

    if (allocated(names)) then
      count = size(names)
    else
      count = 2
    end if

    if (allocated(names)) deallocate(names)
    allocate(character(len=5) :: names(count))
    names = "     "
    if (count >= 1) names(1) = "red"
    if (count >= 2) names(2) = "blue"
  end subroutine replace_names
end module character_names
```

The generated `.pyi` represents a fixed-length rank-one character array as
`String[4][::]`. A deferred-length allocatable rank-one array uses the two-axis
handle spelling `Allocatable[String[:][:]]`, so the element width can come from
the native allocation at runtime:

```python
from x2py.contracts import Allocatable, Returns, String

def make_names() -> Allocatable[String[:][:]]: ...

def replace_names(
    names: Allocatable[String[:][:]]
) -> Returns[
    "names", Allocatable[String[:][:]]
]: ...
```

Build the example:

```bash
python3 -m x2py character_allocatables.f90 --out-dir build/character_allocatables
```

Pass an existing compatible allocatable character handle. The projected result
is that same handle, and extraction remains explicit:

```python
import sys
sys.path.insert(0, "build/character_allocatables")
import character_allocatables

api = character_allocatables.character_names
names = api.make_names()
assert api.replace_names(names) is names
assert names.to_numpy().dtype.itemsize == 5
assert names.to_numpy().tolist() == [b"red  ", b"blue "]
```

The `S5` itemsize comes from `allocate(character(len=5) :: names(count))`.
Plain NumPy arrays are not allocatable descriptors and are rejected for this
handle-typed parameter. When extracting character storage, x2py uses NumPy
bytes dtype `S`; Unicode (`U`) and object (`O`) arrays are not descriptor-handle
substitutes.

Projected writable descriptor mutation requires a handle with persistent
wrapper-owned standard-descriptor storage, such as the owned result returned by
`make_names()`. A borrowed module handle can be passed to a read-only descriptor
argument through descriptor facts, but it cannot be passed to a projected
writable descriptor argument: native mutation of a call-local reconstructed
descriptor would not update the module handle reliably.

## Module Handles And Views

An allocatable module array is native-owned. Reading the Python attribute
returns an `Allocatable[T[...]]` handle, not `ndarray | None`. The module's
allocation routines create and release the storage. `h.to_numpy()` returns the
current live view or `None` according to the current allocation state. When the
Fortran declaration has `target`, the generated `.pyi` marks the handle with
`Aliased`. `Aliased` is not an ownership mode or an extraction selector; it
records native addressability for pointer association, raw-address, foreign-pointer,
and related policy.

A plain allocatable module array has the same extraction contract as an
`Aliased` one. The wrapper uses the completed descriptor mechanism to inspect
the current allocation without copying. If the backend cannot expose a live
view through a supported mechanism, wrapper readiness blocks with a clear
diagnostic. Call `.copy()` explicitly when independent Python-owned storage is
required.

A supported allocatable component belongs to its containing native derived-type
instance. The generated wrapper owns that native instance. The field exposes an
`Allocatable[T[...]]` handle that retains the parent wrapper. Any borrowed NumPy
view produced by `to_numpy()` retains the field handle, and the field handle
retains the parent wrapper. Assigning a replacement array directly to such a
field is rejected when native reallocation must go through an explicit method.

Neither owner model can invalidate an already-created NumPy object safely after
native reallocation. Copy before any operation that may reallocate or
deallocate:

```python
independent = view.copy()
```

## Limitations

- A wrapper-owned allocatable scalar derived result can be passed to a
  compatible ordinary, target, allocatable, allocatable-target, input-only
  pointer, or value dummy. The generated typed holder preserves the same Python
  object and writes allocation changes back to that holder.
- An allocatable scalar derived module variable is a live nullable field proxy,
  and it can satisfy a compatible allocatable dummy through a scoped
  `move_alloc` transaction. The allocation is moved into an exact typed local
  holder, passed to the native procedure, and restored exactly once; no object
  address substitutes for the module descriptor and no descriptor crosses the
  interoperable boundary.
- The complete ordinary, `TARGET`, `ALLOCATABLE`, `ALLOCATABLE,TARGET`,
  `POINTER`, and `VALUE` compatibility rules—including empty state,
  multi-argument cleanup, and deliberate errors—are in the later Wrapping
  Derived Types guide under “Scalar Actuals And Native Dummies.”
- Mutable scalar deferred-length character storage is blocked.
- Plain derived module objects use typed module-specific member access;
  `Aliased` is needed only for policies that require a direct native address.
  Allocatable module-array handles use their standard descriptor path and have
  the same live-view extraction contract with or without `Aliased`.
- Borrowed module handles do not provide the persistent direct descriptor
  handoff required by projected writable descriptor arguments; use an owned
  result handle for that operation.
- An edited `.pyi` cannot relabel a native-owned descriptor as Python-owned.
  Use an implemented owned-result handle or copy an extracted NumPy value when
  Python needs independent storage.
- `Annotated[T[...], Allocatable]` is no longer the active public spelling for
  allocatable array descriptors; use `Allocatable[T[...]]`.

## Evidence And Troubleshooting

Owned results, module and component handles, unallocated state, extraction, and
owner retention are exercised by
[`test_allocatable_views.py`](../../../tests/wrapper/fortran/module_state/test_allocatable_views.py).
Allocatable descriptor `intent(inout)` mutation and same-handle projection are
exercised by
[`test_allocatable_replacement.py`](../../../tests/wrapper/fortran/module_state/test_allocatable_replacement.py).
Character descriptor generation in source and generated-`.pyi` modes is
exercised by
[`test_character_arguments.py`](../../../tests/wrapper/fortran/strings/test_character_arguments.py).

A borrowed view can become stale after its native owner reallocates or
deallocates storage, so copy any data that needs an independent lifetime.
Memory Management expands this rule later, and Runtime Issues later covers
dtype, rank, and stale-storage symptoms.
