---
title: Wrapping Derived Types
audience: users, advanced users
prerequisites: wrapping modules, data types
related: memory-management.md, generic-interfaces.md, fortran-wrapper.md
status: maintained
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

The complete example shows inout mutation and a wrapper-owned function result.

## Fields And Nested Components

Public supported scalar fields become Python descriptors. Private fields are
omitted. A nested scalar derived component is a borrowed child wrapper: it
retains its parent owner and never destroys the component independently.

Allocatable fields use borrowed NumPy views. Pointer fields use
the snapshot-or-block policy. Arrays of derived types are blocked because element
construction, destruction, layout, aliasing, and copy policy are incomplete.

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
methods by
[`test_derived_type_methods.py`](../../../tests/wrapper/fortran/derived_types/test_derived_type_methods.py),
constructors/finalizers by
[`test_constructors_and_finalizers.py`](../../../tests/wrapper/fortran/derived_types/test_constructors_and_finalizers.py),
and borrowed finalization by
[`test_borrowed_finalizers.py`](../../../tests/wrapper/fortran/derived_types/test_borrowed_finalizers.py).

Treat nested child wrappers as borrowed from their containing wrapper rather
than independently owned native objects. Memory Management later expands
ownership, and Error Handling later covers constructor, type, and readiness
failures.
