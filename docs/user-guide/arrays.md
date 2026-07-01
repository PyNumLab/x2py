---
title: Arrays
audience: users
prerequisites: data types, wrapping functions
related: allocatable-arrays.md, pointer-arguments.md, wrapping-subroutines.md
status: maintained
---

# Arrays

Numeric Fortran arrays cross the Python boundary as NumPy arrays. The semantic
contract records element dtype, rank, known extents, layout, allowed strides,
mutability, and storage category. The wrapper validates these facts before the
native call and does not silently repair an incompatible array.

## Complete Array Example

Create `arrays.f90`:

```fortran
module array_ops
  implicit none
contains
  subroutine scale_matrix(rows, columns, values)
    integer(4), intent(in) :: rows, columns
    real(8), intent(inout) :: values(rows, columns)
    values = 2.0_8 * values
  end subroutine scale_matrix

  subroutine shift(size, values)
    integer(4), intent(in) :: size
    real(8), intent(inout) :: values(0:size-1)
    values = values + 1.0_8
  end subroutine shift

  function automatic_vector(size) result(values)
    integer(4), intent(in) :: size
    real(8) :: values(size)
    integer(4) :: index

    values = [(2.0_8 * index, index = 1, size)]
  end function automatic_vector
end module array_ops
```

Inspecting `arrays.f90` prints these array contracts:

```python
@native_call([Ref(Arg(0)), Ref(Arg(1)), Arg(2)])
def scale_matrix(
    rows: Const(Int32),
    columns: Const(Int32),
    values: Annotated[Float64[rows, columns], ORDER_F]
) -> None: ...

@native_call([Ref(Arg(0)), Arg(1)])
def shift(
    size: Const(Int32),
    values: Float64[size - 1 - 0 + 1]
) -> None: ...

@native_call([Ref(Arg(0))])
def automatic_vector(
    size: Const(Int32)
) -> Float64[size]: ...
```

Build it:

```bash
python3 -m x2py arrays.f90 --out-dir build/arrays
```

Then assert in-place mutation, lower-bound handling, and an array result:

```python
import sys

import numpy as np

sys.path.insert(0, "build/arrays")
import arrays

api = arrays.array_ops
matrix = np.ones((2, 3), dtype=np.float64, order="F")
api.scale_matrix(np.int32(2), np.int32(3), matrix)
np.testing.assert_array_equal(matrix, np.full((2, 3), 2.0, order="F"))

shifted = np.zeros(4, dtype=np.float64)
api.shift(np.int32(4), shifted)
np.testing.assert_array_equal(shifted, np.ones(4, dtype=np.float64))

result = api.automatic_vector(np.int32(4))
np.testing.assert_array_equal(
    result,
    np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64),
)
```

## Read The Contract

For the complete example, generated annotations record a rank-two matrix whose
extents depend on `rows` and `columns`, a rank-one lower-bound-aware array, and
an automatic rank-one result. Other supported contracts can use `Float64[:]`,
`Float64[3]`, `Float64[::]`, `Float64[Flat]`, or `Float64[...]`.

The element name maps to an exact NumPy dtype; see [Data Types](data-types.md).
Dimension expressions constrain extents. Python remains zero-indexed even when
the native declaration has non-default lower bounds.

## Validation

Before entering native code, x2py checks:

- exact NumPy dtype without implicit casts;
- native byte order and alignment;
- required rank and every expressible extent;
- contract-required contiguity, orientation, and stride pattern; and
- writeability for output and inout storage.

Read-only arrays are valid for input-only arguments. x2py does not byte-swap,
realign, de-alias overlapping arrays, or make a hidden contiguous copy for an
ordinary in-place contract. A violation raises `TypeError` before native code
runs.

## Layout And Strides

Use `numpy.asfortranarray` or `order="F"` for a multidimensional contract that
requires Fortran orientation, as shown by `matrix` in the complete example.

Rank-one contiguous arrays can satisfy their documented contiguous contract
without a meaningful row/column distinction. Legacy fixed-form array contracts
are contiguous-only. A modern Fortran dummy is stride-aware only when its
generated contract explicitly permits strides. Inspect `.pyi` output instead
of assuming every slice is accepted.

Zero-sized dimensions are supported when dtype, rank, writeability, and known
extent rules still match. Degenerate strides on axes with no addressable
movement do not by themselves make the layout invalid.

## Inputs, Outputs, And Inout Arrays

- Input arrays remain caller-owned and may be read-only.
- Ordinary output arrays remain visible; the caller allocates writable storage.
- Inout arrays remain visible and mutate in place.
- Array function results and allocatable outputs are Python-owned copies.
- Supported pointer results are snapshot copies.
- Borrowed allocatable module or component views are explicitly native- or
  wrapper-owned and require lifetime care.

Caller-provided output storage is demonstrated with complete source in
[Wrapping Subroutines](wrapping-subroutines.md#complete-output-example).

## Assumed Size And Lower Bounds

`Float64[Flat]` records supported flat assumed-size storage. Python supplies
the actual allocation, and the caller must ensure it is large enough for the
native routine. x2py validates explicit dimensions it can express but cannot
infer an omitted final extent from an unrelated argument.

Non-default native lower bounds change how extents are computed internally, 
but they do not alter Python indexing. Even if a Fortran argument is declared 
with custom bounds like values(3:size+2), 
the wrapped NumPy array in Python remains strictly zero-indexed.

## Assumed Rank

Supported numeric assumed-rank arguments accept NumPy ranks 1 through 15 through
a generated native rank dispatcher. Each assumed-rank argument dispatches at
its own runtime rank. Rank-zero values and ranks above 15 are rejected.

## Array Results

Supported numeric array results preserve dtype, rank, and Fortran-oriented
multidimensional data. Allocated zero-sized results are arrays; unallocated
allocatable or unassociated pointer results are `None`.

## Unsupported Forms

- assumed type `type(*)`;
- character arrays;
- arrays of derived types;
- general borrowed pointer array views and reassociation; and
- any kind or rank whose portable NumPy storage contract cannot be proved.

## Evidence And Troubleshooting

Validation and layout behavior are exercised by
[`test_array_contracts.py`](../../tests/wrapper/fortran/arrays/test_array_contracts.py),
assumed-rank behavior by
[`test_assumed_rank_arrays.py`](../../tests/wrapper/fortran/arrays/test_assumed_rank_arrays.py),
multidimensional behavior by
[`test_multidimensional_arrays.py`](../../tests/wrapper/fortran/arrays/test_multidimensional_arrays.py),
and results by
[`test_array_results.py`](../../tests/wrapper/fortran/arrays/test_array_results.py).

When a call fails, compare `value.dtype`, `value.shape`, `value.strides`,
`value.flags`, and writeability with the generated annotation. Continue with
[Runtime Issues](../troubleshooting/runtime-issues.md) if they appear to match.
