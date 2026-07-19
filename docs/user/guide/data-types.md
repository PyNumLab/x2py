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
python3 -m x2py generate --pyi numeric_types.f90
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
| scalar character | `String` or `String[n]` | `str` | fixed-width NumPy bytes, such as `S8` |
| derived type | generated class name | instance of that generated class | arrays of derived types are unsupported |
| dummy procedure | named `@prototype` reference | Python callable matching the named prototype | not applicable |

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

A bare numeric semantic type is a Python-visible value. `T` is a value
contract, not a copy of Fortran `intent`. Its default native boundary is
pass-by-value.
`Addr(Arg(...))` in `@native_call` means x2py converts that Python-visible value
to call-local native scalar storage and passes the storage address to native
code.

Use `T[()]` when the Python API itself exposes safe caller-provided scalar
storage as a rank-0 NumPy array. Use `Addr(T)` only when the caller passes a raw
address such as `array.ctypes.data`. For raw array addresses such as
`Addr(Float64[n])`, every extent must be a fixed literal or a visible argument;
the address value itself does not carry shape. x2py does not reject zero or
negative integer addresses or validate that raw-address extents are positive.
It reports integer-to-pointer overflow, but otherwise the caller is responsible
for supplying a live address and a valid pointee shape before native code uses
either value.

Arrays and strings are storage-like at the native boundary. `Float64[n]` already
passes the NumPy data address, and `String[8]` already passes the address of
x2py's temporary fixed-width character storage. Do not add `Addr(Arg(...))` for
those arguments.

These annotations describe the native contract, not implicit Python
conversions. Use exact NumPy scalar types where the generated call requires
them. Scalar `intent(out)` values are normally hidden and returned as values;
caller-provided writable scalar storage is an explicit advanced `.pyi`
contract, not the default source-generated interface.

Internally x2py treats the Python-extension extraction step and the native handoff step
as two different completed policies:

| `.pyi` contract shape | Python barrier | Native barrier |
| --- | --- | --- |
| `T` | read a Python scalar value | pass the value or call-local scalar storage selected by policy |
| `@native_call([Addr(Arg(i))])` on bare `T` | read a Python scalar value | pass the address of call-local scalar storage |
| `T[()]` | validate rank-0 NumPy scalar storage | pass the caller-provided storage address |
| `T[:]`, `T[n]`, `T[:, :]` | validate NumPy array storage | pass the packed array descriptor/data contract |
| `String[n]` | read a Python `str` | pass x2py's call-local fixed-width character storage |
| `String[n][:]`, `String[:][:]` | validate NumPy bytes array storage | pass the character array descriptor/data contract |
| `Addr(T)` or `Addr(T[n])` | read a raw address value | pass that raw address unchanged |

Those barrier actions are completed after semantic IR is loaded and before
wrapper lowering. Generated bridges and bindings dispatch from the completed
actions; they do not reinterpret datatype, `intent`, addressability, or local
memory details to choose a different behavior.

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
before Python AST normalization. Multidimensional dense arrays in a
Fortran-facing contract use Fortran orientation by default; generated contracts
omit `ORDER_F`. Explicit order metadata appears only when a contract
deliberately requests a non-default representation.

The wrapper validates exact dtype, native byte order, rank, known extents,
alignment, layout, and writeability before entering native code. It does not
silently cast, byte-swap, realign, or repair an incompatible array. Arrays later
expands layout, stride, output-storage, and zero-size rules.

## Strings

Scalar Fortran character values use Python `str`. `String[8]` records fixed
native length eight; plain `String` records assumed, deferred, or otherwise
non-fixed scalar length. The first `String[...]` subscription is character
length, not array shape. Bare `String[:]` is invalid; write `String` for a
scalar non-fixed string or add a second shape axis for an array.

| Contract | Meaning |
| --- | --- |
| `String` | scalar string with unknown, assumed, deferred, or otherwise non-fixed length |
| `String[8]` | scalar fixed-length string with length 8 |
| `String[:][:]` | rank-one array of strings whose element length is not fixed in the public contract |
| `String[8][:]` | rank-one array of fixed-length strings |
| `String[8][()]` | mutable scalar fixed-length string storage |

For `String[8]`, the encoded Python string length must be exactly eight; pass
`"aa      "` when the native argument is an eight-character value.

Returned strings are Python-owned copies. Fixed-length results retain trailing
Fortran blanks. For mutable scalar character input/output, x2py creates
call-local character storage, passes its address to native code, and returns a
replacement only when the `.pyi` signature includes `Returns["name", String[n]]`.
Without that return contract, native mutation is discarded because the original
Python `str` is immutable.

Mutable scalar character storage uses a rank-zero fixed-width NumPy bytes array:

```python
label = np.array("abcdefgh", dtype="S8")
```

The matching `.pyi` annotation is `String[8][()]`. Native mutation writes back
into the NumPy array, and Python reads the scalar storage as bytes, for example
`label[()]`.

Character arrays use fixed-width NumPy bytes dtypes. `String[8][:]` is a rank-one
array of eight-character elements. `String[:][:]` is a rank-one array whose
element length is not fixed in the public contract. For `character(len=5) ::
names(:)`, Python passes and receives arrays with `dtype="S5"`. For an
allocatable deferred-length character array, the runtime allocation length
becomes the returned dtype itemsize. x2py treats these arrays as raw fixed-width
bytes storage; Python Unicode arrays, object arrays, and mutable scalar
deferred-length character storage remain blocked.

## Derived Types

A supported Fortran derived type becomes a generated Python extension class.
Scalar inputs accept that exact generated class or a supported descendant where
polymorphic dispatch is documented. Scalar outputs and function results become
wrapper-owned instances. Nested derived components are borrowed child wrappers
whose parent remains their owner. Do not treat a nested child as independently
owned native storage. Wrapping Derived Types later expands nested-object and
finalization behavior.

## Unsupported Widths And Forms

The semantic format can represent names such as `Float128` and `Complex256`,
but representation in a `.pyi` file is not a native binding support claim. Current
Fortran wrapper generation blocks:

- real storage wider than 64 bits;
- complex storage wider than 128 total bits;
- wider explicit logical storage without a portable NumPy round trip;
- unsigned Fortran integer assumptions without a proved native mapping;
- character arrays that cannot be represented as fixed-width NumPy bytes
  storage; and
- arrays of derived types.

The language feature matrix later records the support status and evidence for a
wrapper-planning error.

## Evidence And Troubleshooting

Scalar integer, logical, real, and complex mappings are exercised by
[`test_scalar_kinds.py`](../../../tests/wrapper/fortran/scalars/test_scalar_kinds.py).
String behavior is exercised by
[`test_character_arguments.py`](../../../tests/wrapper/fortran/strings/test_character_arguments.py),
and array dtype validation by
[`test_array_contracts.py`](../../../tests/wrapper/fortran/arrays/test_array_contracts.py).

For a wrong scalar or array dtype, compare the value with `--pyi` output and
convert explicitly at the Python call site. Runtime Issues later covers a
successful build that rejects a call, while Compiler Issues covers kind probing
and compiler-selection failures.
