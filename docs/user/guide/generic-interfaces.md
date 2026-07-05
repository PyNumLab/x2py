---
title: Generic Interfaces
audience: users, advanced users
prerequisites: wrapping functions, wrapping subroutines, data types
related: optional-arguments.md, wrapping-derived-types.md, error-handling.md
status: maintained
---

# Generic Interfaces

Named module and type-bound generic interfaces become one Python-visible
callable backed by a checked overload set. Dispatch uses exact scalar or array
dtype, rank, and generated extension class; it does not perform broad numeric
coercion.

## Complete Generic Example

Create `generic.f90`:

```fortran
module conversions
  implicit none
  interface convert
    module procedure convert_integer
    module procedure convert_real
  end interface convert
contains
  integer(4) function convert_integer(value) result(output)
    integer(4), intent(in) :: value
    output = value + 10
  end function convert_integer

  real(8) function convert_real(value) result(output)
    real(8), intent(in) :: value
    output = value + 0.5_8
  end function convert_real
end module conversions
```

Inspecting `generic.f90` prints the private specifics and public overload
contracts:

```python
from x2py.contracts import Addr, Arg, Float64, Int32, native_call, overload, private

@private
@native_call([Addr(Arg(0))])
def convert_integer(
    value: Int32
) -> Int32: ...

@private
@native_call([Addr(Arg(0))])
def convert_real(
    value: Float64
) -> Float64: ...

@overload("convert_integer")
@native_call([Addr(Arg(0))])
def convert(
    value: Int32
) -> Int32: ...

@overload("convert_real")
@native_call([Addr(Arg(0))])
def convert(
    value: Float64
) -> Float64: ...
```

Build it:

```bash
python3 -m x2py generic.f90 --out-dir build/generic
```

The public generic dispatches by exact dtype:

```python
import sys
import numpy as np

sys.path.insert(0, "build/generic")
import generic

api = generic.conversions
assert api.convert(np.int32(4)) == np.int32(14)
assert api.convert(np.float64(4.0)) == np.float64(4.5)
```

## Calling A Generic

The complete example covers integer and real overloads. Complex, array, and
generated-class overloads follow the same exact dtype/rank/class rule when
their specifics are supported.

The generated `.pyi` contains overload declarations associated with concrete
native targets. The public generic name remains one callable.

## Type-Bound Generics

Type-bound overloads dispatch after accounting for the implicit passed object.
For example, one documented generated method may provide distinct `Int32` and
`Float64` call shapes under the same public name.

Supported scalar polymorphic input dispatch uses the generated base and
descendant wrapper classes. Descendants are checked before the base class so a
concrete descendant selects its concrete bridge.

## No Match And Ambiguity

A value with no matching specific raises `TypeError`. If two native specifics
collapse to the same Python dtype/rank/class signature, wrapper generation
rejects the overload set deterministically. Declaration order is never used as
an ambiguity tiebreaker.

Changing an overload set in an edited semantic `.pyi` must preserve distinct
supported signatures and valid native targets. Removing an overload removes
that Python call shape; it does not remove the native implementation.

## Defined Operators

Defined operators use Python data-model slots only where Python has equivalent
syntax. Supported arithmetic, unary, comparison, reverse, and safe in-place
forms can therefore appear as normal Python operations such as `left + right`
or a reverse operation when the native specifics define that operand order.

Named native operators without Python syntax become documented methods rather
than invented operators.

## Defined Assignment

Python `=` rebinds a name and cannot invoke native defined assignment. x2py
exposes supported native assignment as an explicit mutating `assign(...)`
method that returns the same receiver object.

Named generics and operator/assignment lowering are separate contracts even
though both use overload dispatch.

## Limitations

- Generic constructor interfaces and overloaded runtime initialization are
  blocked.
- Polymorphic results, mutable polymorphic arguments, arrays, pointer/allocatable
  polymorphic scalars, and `class(*)` are blocked.
- Unsupported operands raise deterministic Python errors; x2py does not fall
  back to a different specific.

## Evidence And Troubleshooting

Named and type-bound generic dispatch is exercised by
[`test_generic_interfaces.py`](../../../tests/wrapper/fortran/naming/test_generic_interfaces.py),
operator and assignment behavior by
[`test_defined_operators.py`](../../../tests/wrapper/fortran/naming/test_defined_operators.py),
and scalar inheritance dispatch by
[`test_inheritance.py`](../../../tests/wrapper/fortran/derived_types/test_inheritance.py).

For `TypeError`, compare the argument dtype, rank, and class with generated
overloads. For generation-time ambiguity, rename or redesign the native call
shapes; declaration reordering is not a fix.
