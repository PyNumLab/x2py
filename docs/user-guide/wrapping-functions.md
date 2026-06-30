---
title: Wrapping Functions
audience: users
prerequisites: data types, first wrapped function
related: wrapping-subroutines.md, arrays.md, fortran-wrapper.md
status: maintained
---

# Wrapping Functions

A Fortran function becomes a Python callable whose direct function result is
the first Python result. Inputs retain the exact dtype, rank, shape, and storage
contract shown by generated `.pyi` output.

Reuse `scale.f90`, whose complete source is first shown in the
[README Quick Start](../../README.md#quick-start) and then explained by
[First Wrapped Function](../getting-started/first-wrapped-function.md). Inspect
that same file before rebuilding it:

```bash
python3 -m x2py scale.f90 --pyi
python3 -m x2py scale.f90 --wrap-readiness
python3 -m x2py scale.f90 --wrap --out-dir build/scale --json
```

## Scalar Functions

The beginner `scale` example generates this callable contract:

```python
@external
def scale(
    value: Ptr(Const(Float64)),
    factor: Ptr(Const(Float64)),
) -> Float64: ...
```

Call it with the resolved NumPy dtype:

```python
result = scale.scale(np.float64(3.0), np.float64(2.5))
assert result == np.float64(7.5)
```

Contained module functions appear on their generated child module instead of
the extension root. Standalone procedures carry `@external` in the semantic
contract. These placement details do not change the Python argument types.

Supported scalar function results include resolved signed integer, real,
complex, logical, scalar character, and supported derived-type values. Read
[Data Types](data-types.md) for the complete mapping. Scalar character results
are Python-owned `str` values; derived results are wrapper-owned generated
class instances.

## Array Results

Numeric explicit-shape, automatic-shape, allocatable, and supported pointer
array results become NumPy arrays. Ordinary and allocatable results are detached
Python-owned copies. Supported pointer results are snapshot copies, not live
views of native targets. The complete `arrays.f90` source, build command, and
asserted result are presented in [Arrays](arrays.md#complete-array-example).

Allocated zero-sized results are zero-sized arrays. An unallocated allocatable
result or unassociated pointer result is `None`. Multidimensional results retain
Fortran-oriented element ordering. See [Arrays](arrays.md) and
[Allocatable Arrays](allocatable-arrays.md) before relying on result lifetime.

## Functions With Output Arguments

If a function also has output dummies, Python returns a tuple. The direct
function result is first, followed by projected output dummies in native
argument order. The `outputs.f90` example in
[Wrapping Subroutines](wrapping-subroutines.md#complete-output-example) shows
the output-dummy part of this projection with complete source and results.

Caller-provided output arrays remain arguments because the caller must allocate
their storage. Their return projection, when present, refers to that same
object. [Wrapping Subroutines](wrapping-subroutines.md) defines the common
`intent(out)` and `intent(inout)` rules.

## Call Limits

- Exact input dtype is required where the generated contract names one; x2py
  does not silently narrow or widen a native scalar or array.
- Numeric array results support ranks 1 through 15. Character arrays and arrays
  of derived types are blocked.
- Wider-than-supported real, complex, or explicit logical storage is blocked
  rather than narrowed.
- A function result never creates an unproven borrowed pointer view.
- Native `stop`, `error stop`, or process abort cannot be converted into a
  normal Python return.

## Evidence And Troubleshooting

Scalar calls are exercised by
[`test_verified_baseline.py`](../../tests/wrapper/fortran/scalars/test_verified_baseline.py),
array results by
[`test_array_results.py`](../../tests/wrapper/fortran/arrays/test_array_results.py),
and mixed result projection by
[`test_output_arguments.py`](../../tests/wrapper/fortran/function_calls/test_output_arguments.py).

For a rejected Python value, compare it with generated `.pyi` output and use
[Runtime Issues](../troubleshooting/runtime-issues.md). For a readiness blocker,
check the [feature matrix](../language-support/feature-matrix.md) before trying
to compile.
