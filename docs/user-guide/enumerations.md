---
title: Enumerations
audience: users
prerequisites: wrapping modules, data types
related: wrapping-modules.md, generic-interfaces.md, ../language-support/feature-matrix.md
status: maintained
---

# Enumerations

Supported Fortran enumerators become typed integer constants. x2py does not
generate Python `Enum` or `IntEnum` classes, and values passed through
procedures or fields remain the resolved integer dtype.

## Complete Enumeration Example

Create `colors.f90`:

```fortran
module colors_api
  implicit none
  enum, bind(C)
    enumerator :: red = -1
    enumerator :: blue
    enumerator :: green = 10
    enumerator :: yellow
  end enum
contains
  integer(4) function round_trip_color(value) result(output)
    integer(4), intent(in) :: value
    output = value
  end function round_trip_color
end module colors_api
```

Build it:

```bash
python3 -m x2py colors.f90 --out-dir build/colors
```

The generated constants retain explicit and implicit values:

```python
import sys
import numpy as np

sys.path.insert(0, "build/colors")
import colors

api = colors.colors_api
assert api.red == np.int32(-1)
assert api.blue == np.int32(0)
assert api.green == np.int32(10)
assert api.yellow == np.int32(11)
assert api.round_trip_color(np.int32(api.green)) == np.int32(10)
```

## Generated Contract

The semantic `.pyi` exposes constants as `Final[Int32]` values for this
resolved representation. A variable or field holding one of these values still
uses `Int32`; it does not acquire a distinct Python enum type.

The constants are read-only native facts. Python assignment can only shadow a
module attribute; it cannot mutate the native enumerator.

## Naming And Type Checking

Generated names follow the normal visibility, keyword escaping, and collision
policy. Static type checkers see integer constants and integer parameters. Code
that needs a project-specific Python `Enum` may define one in application code
and pass `numpy.int32(member.value)` to the wrapper.

## Limitations

- No runtime validation restricting an integer parameter to declared
  enumerator values unless the native routine performs that validation.
- Unsupported source enum forms stop at parsing, semantic readiness, or wrapper
  readiness instead of being converted into unrelated constants.

## Evidence And Troubleshooting

Value preservation, `Final[Int32]` emission, absence of Python enum classes,
field behavior, and runtime round trip are exercised by
[`test_fortran_enums.py`](../../tests/wrapper/fortran/scalars/test_fortran_enums.py).

Use [Data Types](data-types.md) for integer width and
[Wrapping Modules](wrapping-modules.md) for constant attribute behavior.
