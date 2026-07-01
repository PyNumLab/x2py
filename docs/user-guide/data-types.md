---
title: Data Types
audience: users
prerequisites: common beginner workflow
related: arrays.md, wrapping-derived-types.md, ../reference/semantic-pyi-format.md
status: maintained
---

# Data Types

x2py resolves native Fortran types into explicit semantic types before wrapper
generation. The generated `.pyi` contract shows the resolved type, and Python
callers use the matching NumPy dtype or generated wrapper class. Do not infer a
mapping from a Fortran kind number alone: kind values are compiler-dependent,
so wrapper builds probe the selected compiler.

The first example uses a small file named `numeric_types.f90`. Create it with
the complete source below:

```fortran
module numeric_types
  use iso_fortran_env, only: int32, real64
  implicit none
contains
  integer(int32) function add_one(value) result(output)
    integer(int32), intent(in) :: value
    output = value + 1
  end function add_one

  real(real64) function double(value) result(output)
    real(real64), intent(in) :: value
    output = 2.0_real64 * value
  end function double

  complex(real64) function conjugate_value(value) result(output)
    complex(real64), intent(in) :: value
    output = conjg(value)
  end function conjugate_value

  logical(kind=1) function invert(flag) result(output)
    logical(kind=1), intent(in) :: flag
    output = .not. flag
  end function invert
end module numeric_types
```

It is highly recommended to generate the type contract first for inspection:

```bash
python3 -m x2py numeric_types.f90 --pyi
```

Build the wrapper with:

```bash
python3 -m x2py numeric_types.f90 --out-dir build/numeric-types
```

Here is how to call the generated module from Python:

```python
import sys
import numpy as np

sys.path.insert(0, "build/numeric-types")
import numeric_types

api = numeric_types.numeric_types

assert api.add_one(np.int32(4)) == np.int32(5)
assert api.double(np.float64(1.5)) == np.float64(3.0)
assert api.conjugate_value(np.complex128(1.0 + 2.0j)) == np.complex128(1.0 - 2.0j)
assert bool(api.invert(True)) is False
```

The tables below summarize the currently verified Fortran-to-Python type mappings.

## Scalar Mapping

| Fortran storage resolved by the compiler | Semantic `.pyi` type | Python input to prefer | NumPy array dtype |
| --- | --- | --- | --- |
| signed integer, 8 bits | `Int8` | `numpy.int8` | `numpy.int8` |
| signed integer, 16 bits | `Int16` | `numpy.int16` | `numpy.int16` |
| signed integer, 32 bits | `Int32` | `numpy.int32` | `numpy.int32` |
| signed integer, 64 bits | `Int64` | `numpy.int64` | `numpy.int64` |
| real, 32 bits | `Float32` | `numpy.float32` | `numpy.float32` |
| real, 64 bits | `Float64` | `numpy.float64` | `numpy.float64` |
| complex, 64 total bits | `Complex64` | `numpy.complex64` | `numpy.complex64` |
| complex, 128 total bits | `Complex128` | `numpy.complex128` | `numpy.complex128` |
| supported logical storage | `Bool` | `bool` or `numpy.bool_` as documented by the generated contract | `numpy.bool_` |
| scalar character | `String` or `String[n]` | `str` | character arrays are unsupported |
| derived type | generated class name | instance of that generated class | arrays of derived types are unsupported |
| dummy procedure | `Callable[[...], T]` | Python callable with the exact argument/result contract | not applicable |

The checked [First Wrapped Function](../getting-started/first-wrapped-function.md)
uses the same explicit-dtype rule for the smaller `scale.f90` example.

## Source Kind Names

Source spellings such as default `integer`, `integer(8)`,
`integer(kind=int64)`, or a selected-kind expression do not define a portable
NumPy dtype by themselves. x2py resolves the expression with the selected
compiler and then emits `Int8`, `Int16`, `Int32`, or `Int64`. Real, complex,
and logical kinds follow the same rule.

Common `iso_fortran_env` and compiler-supported kind expressions are resolved
during the build. Inspect `--pyi` output whenever compiler flags, the compiler,
or target architecture changes. x2py blocks a mapping that cannot preserve the
native storage instead of silently narrowing it.

## Scalar Values And Native Storage

A bare semantic type is a Python-visible value. `Const(T)` is the read-only
value form. `Ref(Arg(...))` in `@native_call` means x2py passes the
Python-visible value through native reference-backed storage. The generated
declarations for `numeric_types.f90` above demonstrate both value annotations
and native pointer projection.

`Ref(T)` remains the visible annotation when the Python API itself exposes
pointer-like or writable reference-backed storage. Edited native-order
contracts can use that lower-level form directly.

These annotations describe the native contract, not implicit Python
conversions. Use exact NumPy scalar types where the generated call requires
them. Scalar `intent(out)` values are normally hidden and returned as values;
caller-provided writable scalar storage is an explicit advanced `.pyi`
contract, not the default source-generated interface.

## Arrays

Array annotations combine an element dtype with rank and shape:

| Semantic type | Python value |
| --- | --- |
| `Float64[:]` | rank-one dense array with `dtype=numpy.float64` |
| `Float64[:, :]` | rank-two dense array with `dtype=numpy.float64`; the wrapper requires the documented contiguous layout |
| `Float64[::]` | rank-one array whose axis may be a strided NumPy view |
| `Float64[::, ::]` | rank-two array whose axes may be strided NumPy views |
| `Float64[3, 4]` | exact shape `(3, 4)` |
| `Float64[n, :]` | first extent constrained by semantic constant or argument `n` |
| `Float64[Flat]` | flat contiguous storage for a supported assumed-size contract |
| `Float64[...]` | supported assumed-rank numeric storage, ranks 1 through 15 |

Plain `:` records a dense axis. `::` records an axis where the contract allows
runtime strides; x2py reads that exact slice spelling from the `.pyi` source
before Python AST normalization. Multidimensional dense arrays are validated
against their documented orientation, such as `ORDER_F` for Fortran-oriented
storage.

The wrapper validates exact dtype, native byte order, rank, known extents,
alignment, layout, and writeability before entering native code. It does not
silently cast, byte-swap, realign, or repair an incompatible array. See
[Arrays](arrays.md) for layout, stride, output-storage, and zero-size rules.

## Strings

Scalar Fortran character values use Python `str`. `String[8]` records fixed
native length eight; plain `String` records assumed, deferred, or otherwise
non-fixed scalar length. The length is a character length, not an array shape.

Returned strings are Python-owned copies. Fixed-length results retain trailing
Fortran blanks. Mutable scalar character input/output uses replacement: Python
receives a new `str` because the original string is immutable. Character arrays
and mutable deferred-length character storage remain blocked.

## Derived Types

A supported Fortran derived type becomes a generated Python extension class.
Scalar inputs accept that exact generated class or a supported descendant where
polymorphic dispatch is documented. Scalar outputs and function results become
wrapper-owned instances. Nested derived components are borrowed child wrappers
whose parent remains their owner.

Read [Wrapping Derived Types](wrapping-derived-types.md) before retaining nested
objects or using finalizers.

## Unsupported Widths And Forms

The semantic format can represent names such as `Float128` and `Complex256`,
but representation in a `.pyi` file is not a runtime support claim. Current
Fortran wrapper generation blocks:

- real storage wider than 64 bits;
- complex storage wider than 128 total bits;
- wider explicit logical storage without a portable NumPy round trip;
- unsigned Fortran integer assumptions without a proved native mapping;
- character arrays; and
- arrays of derived types.

Check the [language feature matrix](../language-support/feature-matrix.md) when a
generated contract reports a readiness blocker.

## Evidence And Troubleshooting

Scalar integer, logical, real, and complex mappings are exercised by
[`test_scalar_kinds.py`](../../tests/wrapper/fortran/scalars/test_scalar_kinds.py).
String behavior is exercised by
[`test_character_arguments.py`](../../tests/wrapper/fortran/strings/test_character_arguments.py),
and array dtype validation by
[`test_array_contracts.py`](../../tests/wrapper/fortran/arrays/test_array_contracts.py).

For a wrong scalar or array dtype, compare the value with `--pyi` output and
convert explicitly at the Python call site. Use
[Runtime Issues](../troubleshooting/runtime-issues.md) for a successful build
that rejects a call, and [Compiler Issues](../troubleshooting/compiler-issues.md)
when kind probing or compiler selection fails.
