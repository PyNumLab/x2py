---
title: Optional Arguments
audience: users
prerequisites: wrapping subroutines, data types
related: generic-interfaces.md, arrays.md, error-handling.md
status: maintained
---

# Optional Arguments

Supported optional scalars, arrays, strings, derived types, outputs, and inout
arguments preserve native `present(...)` behavior. The generated Python
signature places required parameters before optional parameters without
changing native argument positions.

## Complete Optional Example

Create `optional.f90`:

```fortran
module adjustments
  implicit none
contains
  integer(4) function adjust(value, offset) result(output)
    integer(4), intent(in) :: value
    integer(4), intent(in), optional :: offset

    output = value
    if (present(offset)) output = output + offset
  end function adjust
end module adjustments
```

Inspecting `optional.f90` prints this optional-input contract:

```python
@native_call([Ref(Arg(0)), Ref(Arg(1))])
def adjust(
    value: Const(Int32),
    offset: Const(Int32) = ...
) -> Int32: ...
```

Build it:

```bash
python3 -m x2py optional.f90 --out-dir build/optional
```

Omission and explicit `None` both make `offset` absent:

```python
import sys

import numpy as np

sys.path.insert(0, "build/optional")
import optional

api = optional.adjustments
assert api.adjust(np.int32(5)) == np.int32(5)
assert api.adjust(np.int32(5), None) == np.int32(5)
assert api.adjust(np.int32(5), offset=np.int32(3)) == np.int32(8)
```

## Omission And `None`

For a Python-visible optional input, omission and explicit `None` both mean the
native actual argument is absent. The `adjust` calls above show omission,
explicit `None`, and a concrete keyword value.

A concrete value means the native argument is present. Use keywords when skipping
an earlier optional argument; do not depend on native declaration order after
required and optional Python parameters have been normalized.

## Optional Arrays And Objects

An optional array still requires exact dtype, rank, shape, layout, alignment,
and writeability when supplied. `None` means no native argument; it does not
mean a zero-sized array. An optional derived-type argument accepts `None` or an
instance of the required generated class.

## Optional Outputs

Optional output behavior depends on who supplies storage:

- a supplied caller-provided output array is mutated and returned as documented;
- an absent caller-provided output array contributes `None` to its result
  position;
- a hidden scalar or derived output is requested with generated temporary
  storage and therefore remains present and returned; and
- an optional inout argument mutates normally when supplied and does nothing
  when absent.

Always review the generated return annotation when optional outputs are mixed
with required outputs.

## Defaults

The generated Python default is normally `None`, meaning native absence. x2py
does not invent a native default value from a Python literal unless the semantic
contract explicitly defines that behavior. A native procedure remains
responsible for its own `present(...)` branch.

## Unsupported Combinations

Optional passed procedures, procedure pointers, and combinations without a
complete native presence and ownership contract are readiness blockers. x2py
does not convert an unsupported optional form into an always-present argument
or silently drop it.

## Evidence And Troubleshooting

Optional scalar, array, string, derived, output, and inout behavior is exercised
by
[`test_optional_arguments.py`](../../tests/wrapper/fortran/function_calls/test_optional_arguments.py).

Use [Wrapping Subroutines](wrapping-subroutines.md) for result projection and
[Error Handling](error-handling.md) when an unsupported optional combination
stops at readiness.
