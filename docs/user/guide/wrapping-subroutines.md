---
title: Wrapping Subroutines
audience: users
prerequisites: data types, first wrapped function
related: wrapping-functions.md, arrays.md, optional-arguments.md
status: maintained
---

# Wrapping Subroutines

A subroutine has no direct native function result, but its output arguments may
become Python return values. The generated signature separates hidden values
from the storage that the Python caller must allocate.

## Argument Projection

| Native role | Python call shape | Python result shape |
| --- | --- | --- |
| scalar `intent(in)` | visible exact-type argument | no result |
| scalar `intent(out)` | hidden | returned value |
| immutable scalar replacement | visible input when required | returned replacement |
| array `intent(in)` | visible NumPy array | no result |
| array `intent(out)` | visible writable NumPy array | same array when projected |
| array `intent(inout)` | visible writable NumPy array | mutated in place; not duplicated unless explicitly projected |
| allocatable array `intent(out)` | hidden unless optional | wrapper-owned `AllocatableArray` |
| allocatable array `intent(inout)` | visible `AllocatableArray` argument | same handle when projected; allocation state changes in place |
| supported derived `intent(out)` | hidden | new wrapper-owned instance |

`optional, intent(out)` is the visibility exception for normally hidden
outputs. The argument remains visible so the caller can omit it and make native
`present(...)` false. Optional scalar outputs use mutable rank-zero storage such
as `Int32[()]`. An optional allocatable array argument uses
`Allocatable[T[...]] | None = ...`: omission means native absence, while a
present handle carries allocated or unallocated descriptor state.

The generated `.pyi` is authoritative when a procedure combines several of
these forms.

## Complete Output Example

Create `outputs.f90`:

```fortran
module outputs
  implicit none
contains
  subroutine bounds(values, smallest, largest)
    real(8), intent(in) :: values(:)
    real(8), intent(out) :: smallest, largest

    smallest = minval(values)
    largest = maxval(values)
  end subroutine bounds

  subroutine scale_in_place(values, factor)
    real(8), intent(inout) :: values(:)
    real(8), intent(in) :: factor

    values = factor * values
  end subroutine scale_in_place

  subroutine fill(values)
    real(8), intent(out) :: values(:)
    values = 1.0_8
  end subroutine fill
end module outputs
```

Inspecting `outputs.f90` prints these subroutine contracts:

```python
from x2py.contracts import Addr, Arg, Float64, Return, Returns, native_call

@native_call([Arg(0), Return('smallest', 0), Return('largest', 1)])
def bounds(
    values: Float64[::]
) -> tuple[Float64, Float64]: ...

@native_call([Arg(0), Addr(Arg(1))])
def scale_in_place(
    values: Float64[::],
    factor: Float64
) -> None: ...

def fill(
    values: Float64[::]
) -> Returns["values", Float64[::]]: ...
```

Build the extension:

```bash
python3 -m x2py outputs.f90 --out-dir build/outputs
```

Then assert scalar projection, in-place mutation, and output-array projection:

```python
import sys
import numpy as np

sys.path.insert(0, "build/outputs")
import outputs

api = outputs.outputs
source = np.array([4.0, -2.0, 7.0], dtype=np.float64)
smallest, largest = api.bounds(source)
assert smallest == np.float64(-2.0)
assert largest == np.float64(7.0)

mutable = np.array([1.0, 2.0, 3.0], dtype=np.float64)
assert api.scale_in_place(mutable, np.float64(3.0)) is None
np.testing.assert_array_equal(mutable, np.array([3.0, 6.0, 9.0], dtype=np.float64))

target = np.empty(4, dtype=np.float64)
returned = api.fill(target)
assert returned is target
np.testing.assert_array_equal(target, np.ones(4, dtype=np.float64))
```

## Hidden Scalar Outputs

A non-allocatable scalar output does not require caller storage in the normal
source-generated API. The `bounds` call above returns `smallest` and `largest`
without corresponding Python arguments.

Hidden outputs are returned in native argument order. A hidden scalar character
output becomes a new `str`, and a hidden scalar derived output becomes a new
wrapper-owned object.

In `@native_call`, `Return(...)` always names hidden writable native output
storage. The wrapper passes that storage to the native procedure by address,
because an output argument cannot be written by value. Do not write
`Addr(Return(...))`; `Return(...)` already carries the output-storage contract.

## Caller-Provided Arrays

Array output and inout storage remains visible. Allocate it with the exact
dtype, shape, layout, alignment, and writeability required by the contract. The
`fill` call above returns the same `target` object after native mutation, while
`scale_in_place` mutates `mutable` in place and returns `None`.

The initial contents of an `intent(out)` array are ignored by Fortran, but the array must still be pre-allocated on the Python side.
An `intent(inout)` array is read and written in place. x2py does not create a hidden replacement
for ordinary array storage merely because the supplied array is inconvenient;
an incompatible array is rejected before the native call.

## Multiple Results

For a subroutine, projected results follow the native output argument order. For a function,
the function result comes first, followed by output arguments in native argument
order. A caller-provided output can remain visible and also be named in return
metadata; hidden outputs use ordinary result annotations.

Do not infer tuple order from Python assignment names. Review the generated
`.pyi` and its `Returns[...]` entries when several outputs are present.

## Scalar Mutation

Python numbers and strings are immutable. They cannot expose native in-place
mutation. Source-generated output scalars are returned as values, and supported
character `intent(inout)` uses replacement projection: the original `str`
remains unchanged and Python receives a new string.

An edited semantic contract can deliberately require writable zero-dimensional
NumPy storage for a visible scalar output. That is an advanced native-order
contract, not the normal source-generated subroutine API. Editing Semantic
`.pyi` Contracts explains that advanced form later.

## Limitations

- Pointer scalar output and inout use nullable copied-value projection. Pointer
  array descriptor arguments use `Pointer[T[...]]` handles; pointer results and
  reassociation without completed policy remain blocked.
- Character arrays require fixed-width NumPy bytes dtype storage. Arrays of
  derived types are blocked.
- Allocatable scalar derived-type replacement is blocked.
- Unsupported output combinations stop at readiness; code generation does not
  silently select another projection.

## Evidence And Troubleshooting

Output projection, tuple ordering, caller-provided arrays, allocatable outputs,
and character/derived outputs are exercised by
[`test_output_arguments.py`](../../../tests/wrapper/fortran/function_calls/test_output_arguments.py)
and
[`test_native_call_examples.py`](../../../tests/wrapper/fortran/function_calls/test_native_call_examples.py).

For array validation failures, compare the value with the exact generated
dtype, rank, shape, layout, and writeability contract. Arrays, Memory
Management, and Error Handling expand validation, ownership, and projected
status exceptions later in the guide.
