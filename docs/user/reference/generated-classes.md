---
title: Generated Classes Reference
audience: users, advanced users
prerequisites: wrapping derived types
related: generated-functions.md, generated-modules.md, semantic-pyi-format.md, ../guide/wrapping-derived-types.md, ../guide/memory-management.md
status: maintained
---

# Generated Classes Reference

Supported Fortran derived types become generated Python extension classes.
Instances wrap native storage through x2py's completed ownership policy; Python
field access and methods use generated wrapper operations instead of exposing a
stable binary layout.

Use [Wrapping Derived Types](../guide/wrapping-derived-types.md) for the
source-first workflow and [Memory Management](../guide/memory-management.md)
for ownership vocabulary. This page is the generated class surface reference.

## Class Placement

A derived type declared in a Fortran module is exposed from the generated child
module for that native module:

```python
import geometry

point = geometry.points.point
item = point(x=np.float64(1.0), y=np.float64(2.0))
```

The semantic `.pyi` contract records the public class name, constructor shape,
fields, methods, overloads, native type metadata, and ownership metadata.
Private derived types are omitted unless an edited contract intentionally
changes visibility and remains supported.

## Constructors

x2py generates a keyword-only Python initializer for public rank-zero numeric,
logical, and complex fields that are safe constructor inputs:

```python
from x2py.contracts import Float64, Int32, native_type

@native_type(finalizers=('cleanup_initialized',))
class initialized:
    def __init__(
        self,
        *,
        id: Int32 = 7,
        scale: Float64 = 2.5
    ) -> None: ...

    id: Int32 = 7
    scale: Float64 = 2.5
```

Omitted keywords preserve native default initialization. Private components,
arrays, allocatables, pointers, strings, and nested derived components are not
automatic constructor keywords.

An edited semantic `.pyi` may remove the generated constructor or bind one
concrete initializer. x2py does not recreate a constructor intentionally
removed from the contract. Generic constructor interfaces remain unsupported
when x2py cannot select one deterministic Python initializer.

## Fields And Methods

Supported public scalar fields become Python descriptors. Assigning to a
writable field uses the completed setter policy. Private fields are omitted.

Nested scalar derived components are borrowed child wrappers that retain their
owning parent. Allocatable fields can expose borrowed NumPy views when
ownership and lifetime are explicit. Pointer fields use detached-copy-or-block
policy. Arrays of derived types are unsupported.

Snapshot classes generated for plain derived module variables expose copied data
fields only. They do not expose type-bound procedures or writable setters, and
their `snapshot_type` attribute points at the live wrapper class they snapshot.

Type-bound procedures become methods. The generated semantic contract uses
`Pass()` on the concrete native-specific method when the native passed-object
position is not the default, and `@overload(...)` when a generic method has
multiple specific procedures:

```python
from x2py.contracts import Addr, Arg, Float64, Int32, Pass, bind, native_call, overload, private

class accumulator:
    total: Float64 = 0.0

    @private
    @bind("accumulator_add_integer")
    @native_call([Pass(), Addr(Arg(0))])
    def add_integer(
        self,
        value: Int32
    ) -> None: ...

    @overload("accumulator_add_integer")
    def add(
        self,
        value: Int32
    ) -> None: ...
```

Method dispatch is exact. Indistinguishable overloads or unsupported generic
constructors block generation. The overload declaration is only a Python
dispatch link; it cannot also carry `@native_call(...)`.

## Ownership And Finalization

Generated constructors and wrapper-owned function results allocate native
instances owned by the Python wrapper. The generated deallocator finalizes and
releases that native instance exactly once.

Borrowed child wrappers, borrowed module objects, and borrowed component views
do not destroy the storage they reference. They retain the owning wrapper or
module reference needed for Python lifetime, but explicit native deallocation
or reallocation can still invalidate borrowed storage. `Snapshot[T]` objects are
Python-owned read-only copies and do not retain or mutate native storage.

Native finalizers do not provide a recoverable Python status channel during
object destruction. Use ordinary wrapped procedures for recoverable cleanup
steps that need status reporting.

## Unsupported Class Shapes

x2py blocks derived-type forms whose Python ownership or dispatch policy is not
complete:

- arrays of derived types;
- mutable polymorphic arguments and polymorphic results;
- `class(*)`, abstract instantiation, and deferred bindings;
- allocatable or pointer polymorphic scalars; and
- direct binary-layout access for ordinary generated classes.

When a type is unsupported, the wrapper readiness report should explain the
blocking form instead of generating a partial class.

## Evidence And Maintenance

Generated class behavior is covered by
[`test_derived_type_boundaries.py`](../../../tests/wrapper/fortran/derived_types/test_derived_type_boundaries.py),
[`test_derived_type_methods.py`](../../../tests/wrapper/fortran/derived_types/test_derived_type_methods.py),
[`test_constructors_and_finalizers.py`](../../../tests/wrapper/fortran/derived_types/test_constructors_and_finalizers.py),
[`test_borrowed_finalizers.py`](../../../tests/wrapper/fortran/derived_types/test_borrowed_finalizers.py), and
[`test_inheritance.py`](../../../tests/wrapper/fortran/derived_types/test_inheritance.py).

When class behavior changes, update this page with the derived-type user guide,
semantic `.pyi` reference, generated contract fixtures, and ownership evidence.
