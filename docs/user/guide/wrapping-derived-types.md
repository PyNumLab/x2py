---
title: Wrapping Derived Types
audience: users, advanced users
prerequisites: wrapping modules, data types
related: memory-management.md, generic-interfaces.md, fortran-wrapper.md
status: maintained
publication: draft
---

# Wrapping Derived Types

A supported Fortran-derived type becomes a generated Python extension class.
The wrapper owns an opaque native instance; Python field access and methods use
generated native operations rather than assuming a public memory layout.

## Complete Derived-Type Example

Create `points.f90`:

```fortran
module points
  implicit none
  type :: point
    real(8) :: x = 0.0_8
    real(8) :: y = 0.0_8
  end type point

  type :: holder
    type(point) :: origin
  end type holder
contains
  subroutine move(item, dx, dy)
    type(point), intent(inout) :: item
    real(8), intent(in) :: dx, dy
    item%x = item%x + dx
    item%y = item%y + dy
  end subroutine move

  function make_point(x, y) result(item)
    real(8), intent(in) :: x, y
    type(point) :: item
    item%x = x
    item%y = y
  end function make_point

  subroutine set_origin(container, item)
    type(holder), intent(inout) :: container
    type(point), intent(in) :: item
    container%origin = item
  end subroutine set_origin
end module points
```

Build it:

```bash
python3 -m x2py points.f90 --out geometry --out-dir build/geometry
```

Then construct, mutate, return, and borrow generated objects:

```python
import sys
import numpy as np

sys.path.insert(0, "build/geometry")
import geometry

points = geometry.points
item = points.point(x=np.float64(1.0), y=np.float64(2.0))
points.move(item, np.float64(3.0), np.float64(4.0))
assert item.x == np.float64(4.0)
assert item.y == np.float64(6.0)

made = points.make_point(np.float64(8.0), np.float64(9.0))
assert isinstance(made, points.point)

container = points.holder()
points.set_origin(container, made)
origin = container.origin
origin.x = np.float64(12.0)
assert container.origin.x == np.float64(12.0)
```

## Arguments And Results

- `intent(in)` passes an existing wrapper instance without transferring ownership.
- `intent(inout)` mutates the same native instance.
- hidden `intent(out)` returns a new wrapper-owned instance.
- a function result is copied into a new wrapper-owned native instance before
  the native temporary expires.

When an edited semantic contract keeps a writable derived argument visible and
projects it with `Returns["name", T]`, the return value is the exact same Python
wrapper that the caller supplied. Native code mutates that wrapper's existing
storage; the binding does not construct a replacement object, copy the derived
value, or assume destruction responsibility. Omitting the projection leaves the
same mutation in place and returns only the other declared results (or `None`).

The complete example shows inout mutation and a wrapper-owned function result.

A native by-value argument is preserved in generated semantic contracts as
`@native_call([Value(Arg(0)), ...])`. Python still passes an existing `point`
wrapper.
The generated Fortran bridge imports the exact native type and performs the
typed by-value call. The foreign boundary never lays out or byte-copies the
aggregate,
so the same opaque mechanism applies to exact ordinary, `sequence`, and
`bind(C)` types. Polymorphic or unresolved types remain blocked.

## Scalar Actuals And Native Dummies

This section is the canonical compatibility reference for rank-zero,
monomorphic derived objects. It applies when a wrapper object—including a live
module attribute—is passed to another wrapped Fortran procedure. Arrays and
polymorphic objects follow different rules.

An actual object has one of five relevant Fortran declaration forms:

| Key | Actual declaration |
| --- | --- |
| `O` | `type(item) :: value` |
| `T` | `type(item), target :: value` |
| `A` | `type(item), allocatable :: value` |
| `AT` | `type(item), allocatable, target :: value` |
| `P` | `type(item), pointer :: value` |

A native dummy has six forms:

| Key | Dummy declaration |
| --- | --- |
| `O` | `type(item) :: arg` |
| `T` | `type(item), target :: arg` |
| `A` | `type(item), allocatable :: arg` |
| `AT` | `type(item), allocatable, target :: arg` |
| `P` | `type(item), pointer :: arg` |
| `V` | `type(item), value :: arg` |

`OPTIONAL`, `INTENT`, rank, and the qualified native type are additional facts;
they are not extra declaration rows. In the table, “payload” requires an
allocated allocatable or associated pointer. “Holder” means persistent
wrapper-owned Fortran storage. “Scoped” means the originating module exposes an
address only for the duration of the synchronous native call. “Allocation
transaction” and “pointer transaction” write descriptor or association changes
back to the originating module variable before control returns to Python.

| Actual and origin | `O` dummy | `T` dummy | `A` dummy | `AT` dummy | `P` dummy | `V` dummy |
| --- | --- | --- | --- | --- | --- | --- |
| `O`, wrapper-owned | direct reference | call-scoped target | incompatible | incompatible | input-only pointer adapter | typed value |
| `O`, module | scoped reference | scoped target | incompatible | incompatible | scoped input-only pointer adapter | scoped typed value |
| `T`, wrapper-owned | direct reference | direct target | incompatible | incompatible | input-only pointer adapter | typed value |
| `T`, module | module address | module target | incompatible | incompatible | input-only pointer adapter | typed value |
| `A`, wrapper holder | payload | payload as holder target | allocatable holder | allocatable holder | payload input-only pointer adapter | payload typed value |
| `A`, module | scoped payload | scoped payload target | allocation transaction | allocation transaction with call target | scoped payload input-only pointer adapter | scoped payload typed value |
| `AT`, wrapper holder | payload | payload as holder target | allocatable holder | allocatable holder | payload input-only pointer adapter | payload typed value |
| `AT`, module | module payload address | module payload target | target-preserving allocation transaction | target-preserving allocation transaction | payload input-only pointer adapter | payload typed value |
| `P`, wrapper holder | pointee | pointee target | incompatible | incompatible | pointer holder | pointee typed value |
| `P`, module | module pointee | module pointee target | incompatible | incompatible | pointer transaction | pointee typed value |

“Incompatible” is a deliberate `TypeError` before native entry, not an
unimplemented Phase 8 fallback. A nonpointer actual can satisfy `P` only when
the pointer dummy is proved `INTENT(IN)`. A pointer dummy with no `INTENT`, or
with `INTENT(OUT)`/`INTENT(INOUT)`, may change association and therefore
requires a pointer actual. If the edited contract omits `INTENT` but an imported
Fortran interface is authoritative, x2py emits the target adapter and lets the
Fortran compiler enforce this rule. Without either source of authority, wrapper
generation reports an interface error.

For payload calls, an unallocated `A`/`AT` actual or disassociated `P` actual
raises `ValueError` before native entry. Descriptor dummies `A`, `AT`, and `P`
instead accept empty state so the native procedure can allocate, deallocate,
nullify, or reassociate it. Empty state is still a present argument; only an
omitted optional argument or explicit optional `None` means absence.

### Module Transactions And Multiple Arguments

Module allocation and pointer state stays in Fortran. x2py uses one shared
typed allocatable holder and pointer holder per qualified native type. The
interoperable boundary carries only an opaque holder address and typed operation
pointers; no native descriptor crosses that boundary.

For an allocatable module actual passed to `A` or `AT`, a module operation uses
`move_alloc` to place its allocation in a bridge-local typed holder. The native
procedure receives that holder component, and a cleanup operation moves the
final allocation back exactly once. For a module pointer passed to `P`, a local
pointer holder starts with the current association; cleanup restores its final
association to the module pointer exactly once. A module target needs neither
transaction: its durable native address is sufficient.

A procedure may take any number of scalar-derived arguments. x2py validates all
slots first, acquires module origins in deterministic order, nests scoped
address producers, invokes the native procedure once, and restores transactions
in reverse order. It does not generate `2**N` call variants. Repeated read-only
use of the same object shares one acquisition; ambiguous writable aliasing is
rejected before any module state moves.

This also applies when arguments are module variables from different Fortran
modules and have different qualified derived types. Each module variable owns a
separate bridge operation table and scoped callback; the binding validates the
table's qualified native type before the callback is invoked. There is no
shared type-specific callback slot, so one module variable cannot overwrite
another argument's transport.

If a later acquisition or the native call reports a normal ABI error, cleanup
continues for every acquired origin and Python raises only after the Fortran
frames have returned. Concurrent or recursive use of the same active module
transaction raises `RuntimeError`. A restoration failure also raises
`RuntimeError` and poisons that module proxy rather than pretending its state is
usable. Process termination, `error stop`, signals, and invalid native pointers
cannot be converted into recoverable Python exceptions.

A pointer holder owns its association variable, not its target. Native storage
remains native-owned unless completed policy identifies and retains a known
module, parent, or wrapper target. Destroying the Python holder nullifies its
component and releases only the holder; it never deallocates an unknown target.

## Fields And Nested Components

Public supported scalar fields become Python descriptors. Private fields are
omitted. A nested scalar derived component is a borrowed child wrapper: it
retains its parent owner and never destroys the component independently.
The same readable and, when policy permits, writable descriptor surface is used
for wrapper-owned instances, borrowed objects, and live module objects. A
target/addressable module object may use a direct native address; a plain module
object uses typed member getter and setter operations instead. Neither path
creates a detached whole-object copy.

Allocatable fields expose `Allocatable[T[...]]` handles, and pointer-array
fields expose `Pointer[T[...]]` handles. Each field handle retains the parent
wrapper for descriptor access. Call `to_numpy()` to extract the current NumPy
view or `None`; extraction never copies. Discard old views after native
deallocation, reallocation, nullification, or reassociation because accessing a
stale view is unsupported and may crash. Call `.copy()` explicitly for
independent NumPy storage. Pointer fields use a conservative default operation
policy, while ownership-changing operations require explicit pointer policy.
Arrays of derived types remain blocked because element construction,
destruction, layout, aliasing, and copy policy are incomplete.
Rank-zero allocatable or pointer components whose value is itself a derived
object use the same completed holder and ownership policy when their origin is
supported. Rank-zero allocatable and pointer module variables expose persistent
live descriptor proxies, including while the allocatable is unallocated or the
pointer is disassociated. Payload-field access then raises `ReferenceError`,
but the same proxy can still be passed to an `A`, `AT`, or `P` dummy so native
code can establish new state. Wrapper-owned allocatable and pointer results use
persistent typed holders with the same empty-state rule.
Their complete call compatibility and transaction rules are defined in
[Scalar Actuals And Native Dummies](#scalar-actuals-and-native-dummies). x2py
does not silently turn an unsupported origin into an owned object or detached
copy.

## Constructors

Native allocation runs native default component initialization. x2py generates
a keyword-only Python initializer for public rank-zero numeric, logical, and
complex fields. Omitted keywords preserve the native initialized values.

Private components, arrays, allocatables, pointers, strings, and nested derived
components are not automatic constructor keywords. A type with fields but no
eligible keywords still receives explicit default construction when supported.

An edited semantic `.pyi` may remove the generated constructor or bind one
concrete initializer. x2py does not regenerate a constructor that the edited
contract intentionally removed.

## Finalizers

An owned wrapper invokes native finalization exactly once when its owning Python
wrapper is collected. Failed initialization still releases the allocated native
instance. Borrowed child wrappers do not finalize their component; finalization
belongs to the containing owner.

A native finalizer has no recoverable Python status channel during object
deallocation. Native termination from a finalizer terminates the process.

## Inheritance And Polymorphism

Supported extension types form a matching Python inheritance hierarchy. A
scalar polymorphic input over a known hierarchy dispatches descendant-first.

Ordinary native `class(T)` arguments retain `Annotated[T, Polymorphic]` in the
semantic `.pyi` because that source fact selects the accepted dynamic-type
dispatch. The passed-object dummy of a type-bound procedure is different: its
class binding already proves that it is polymorphic, so generated contracts use
the plain declared type for that one argument and restore the fact when loading
the binding.

Polymorphic results, mutable polymorphic arguments, arrays, allocatable or pointer
polymorphic scalars, `class(*)`, abstract instantiation, and deferred bindings
are blocked.

## Opaque Layout

Generated wrappers do not expose a direct binary-layout promise for ordinary
derived types. Component order and native facts remain in semantic IR, but
Python access follows generated accessors. Do not use `ctypes` offsets or assume
that Python-visible fields imply a stable binary layout.

## Evidence And Troubleshooting

Scalar boundaries and nested lifetime are exercised by
[`test_derived_type_boundaries.py`](../../../tests/wrapper/fortran/derived_types/test_derived_type_boundaries.py),
direct live object and field behavior by
[`test_phase8_derived_plan.py`](../../../tests/wrapper/fortran/derived_types/test_phase8_derived_plan.py),
the complete scalar actual/dummy matrix and multi-argument transactions by
[`test_scalar_derived_actual_dummy_matrix.py`](../../../tests/wrapper/fortran/derived_types/test_scalar_derived_actual_dummy_matrix.py),
methods by
[`test_derived_type_methods.py`](../../../tests/wrapper/fortran/derived_types/test_derived_type_methods.py),
constructors/finalizers by
[`test_constructors_and_finalizers.py`](../../../tests/wrapper/fortran/derived_types/test_constructors_and_finalizers.py),
and borrowed finalization by
[`test_borrowed_finalizers.py`](../../../tests/wrapper/fortran/derived_types/test_borrowed_finalizers.py).

Treat nested child wrappers as borrowed from their containing wrapper rather
than independently owned native objects. Memory Management later expands
ownership, and Error Handling later covers constructor, type, and wrapper-planning
failures.
