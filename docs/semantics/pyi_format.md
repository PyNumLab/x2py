# Wrapper `.pyi` Format

The semantic `.pyi` format is a Python-valid view of x2py semantic IR. It is
language-neutral: Fortran and future C inputs use the same type, storage,
pointer, array, layout and metadata notation. Source language differences are
represented by contracts and metadata, not by separate syntax families.

This document describes the behavior implemented for the current Fortran path
and the shared notation it establishes for later C semantic conversion. C
semantic conversion and C `.pyi` generation remain deferred.

## Canonical Type And Storage Contract

Bare scalar types represent direct semantic values:

```python
def dot_value(a: Float64, b: Float64) -> Float64: ...
```

Native reference and pointer-backed storage is explicit:

```python
def inspect(value: Ptr(Const(Int32))) -> None: ...
def update(value: Ptr(Float64)) -> None: ...
```

Array storage uses NumPy-style subscriptions. The dimensions inside `T[...]`
are the storage contract:

```python
def scale(n: Ptr(Const(Int32)), x: Float64[n]) -> None: ...
def matrix(a: Annotated[Const(Float64[n, m]), ORDER_F]) -> None: ...
def assumed(x: Annotated[Float64[::Strided, ::Strided], ORDER_ANY]) -> None: ...
```

There is no separate dimension helper in canonical type syntax. A dimension
entry without colons is an extent (`Float64[n]`, `Float64[n, m]`). Slice-like
entries express range or stride contracts (`Float64[1:n]`,
`Float64[::Strided]`, `Float64[:, 0:n:m]`). `Strided` means the runtime stride
is part of the accepted storage contract.

`Annotated[...]` carries non-dimensional metadata:

- `ORDER_F` for a Fortran-oriented multidimensional contract.
- `ORDER_ANY` for an orientation-independent multidimensional strided
  contract.
- `Allocatable` for a Fortran allocatable array.
- `Pointer` for a Fortran pointer array.
- `ArrayCategory("...")` for the preserved Fortran dummy category, such as
  `"assumed_shape"`, `"assumed_size"` or `"deferred_shape"`.
- `SourceDims(...)` for the original source-level dimension expressions when
  the public storage dimensions differ from those source expressions.
- `LowerBounds(...)` for non-default source lower bounds.
- `Intent("out")` when a visible exact-native argument has source intent
  `out`; `intent(inout)` is the default writable reference/array spelling and
  does not need metadata.

Plain multidimensional array notation is C-oriented (`ORDER_C`) by default.
Generated Fortran stubs emit `ORDER_F` only when rank and orientation make it
observable. Rank-one contiguous storage has no C-versus-Fortran order
distinction, so no order marker is emitted for vectors.

## Implemented Fortran Exact Form

Generated Fortran `.pyi` currently represents the exact native dummy-argument
interface. It does not synthesize, reorder or hide arguments and it does not
turn `intent(out)` or `intent(inout)` dummy arguments into Python return
values.

Fortran scalar dummy arguments are represented as follows:

- Scalar dummy without `value`, `intent(in)`: `Ptr(Const(T))`.
- Scalar dummy without `value`, `intent(out)` or `intent(inout)`: `Ptr(T)`.
- Scalar dummy with `value`: direct `T`.
- Function result: direct return annotation.

Example:

```fortran
subroutine update(scale, value, result)
  real(8), value, intent(in) :: scale
  real(8), intent(inout) :: value
  real(8), intent(out) :: result
end subroutine
```

```python
def update(
    scale: Float64,
    value: Ptr(Float64),
    result: Annotated[Ptr(Float64), Intent("out")]
) -> None: ...
```

Fortran module variables and derived-type fields are data declarations, not
procedure dummy arguments. Scalar fields and variables therefore remain direct
types:

```python
answer: Final[Int32]

class particle:
    id: Int32
    position: Float64[3]
```

## Implemented Fortran Arrays

Explicit-shape and adjustable arrays use shaped storage. Multidimensional
Fortran-contiguous storage carries `ORDER_F`; vectors omit order metadata:

```python
def scale(n: Ptr(Const(Int32)), x: Float64[n]) -> None: ...

def apply(
    n: Ptr(Const(Int32)),
    m: Ptr(Const(Int32)),
    a: Annotated[Const(Float64[n, m]), ORDER_F],
) -> None: ...
```

Assumed-size arrays preserve the known rank and the missing final extent
boundary. A rank-one `x(*)` is emitted as `T[:]`; multidimensional forms keep
the known dimensions and source category metadata:

```python
def legacy(values: Float64[:]) -> None: ...

def legacy_matrix(
    n: Ptr(Const(Int32)),
    a: Annotated[Float64[n, :], ORDER_F, ArrayCategory("assumed_size"), SourceDims("n", "*")]
) -> None: ...
```

Assumed-shape arrays are stride-aware. A rank-one assumed-shape dummy is
emitted as a strided vector. A rank-two or higher unrestricted assumed-shape
dummy uses `ORDER_ANY`:

```python
def vector(x: Annotated[Float64[::Strided], ArrayCategory("assumed_shape"), SourceDims(":")]) -> None: ...

def matrix(
    a: Annotated[
        Const(Float64[::Strided, ::Strided]),
        ORDER_ANY,
        ArrayCategory("assumed_shape"),
        SourceDims(":", ":"),
    ]
) -> None: ...
```

`contiguous` assumed-shape arrays use dense dimensions instead of
`::Strided`; multidimensional forms carry `ORDER_F`.

Allocatable and pointer arrays preserve their source storage property:

```python
class workspace:
    values: Annotated[Float64[:], Allocatable, ArrayCategory("deferred_shape")]

def section(
    x: Annotated[Float64[::Strided], Pointer, ArrayCategory("deferred_shape")]
) -> None: ...
```

Allocation or association replacement policy is not implemented. The semantic
IR preserves the facts needed for readiness and lowering decisions; a backend
must not silently treat replacement-capable allocatable or pointer dummies as
ordinary borrowed arrays.

## Preserved Metadata

The shared semantic model separates:

- value type (`Float64`, `Int32`, derived type names);
- storage/calling contract (`value`, `reference`, `pointer`, `array`);
- array contract (rank, dimensions, source dimensions, lower/upper bounds,
  order, contiguity, category, allocatable, pointer);
- source origin metadata (source language, native name, native scope,
  source-level type/category information and lowering-relevant facts).

The Fortran converter currently preserves rank, public storage dimensions,
source dimension expressions, non-default lower bounds, dummy category,
`intent`, optionality, `value`, constants, `allocatable`, `pointer` and
`contiguous` where the parser supplies those facts.

## Loading And Round Trips

`parse_pyi_text`, `load_pyi_file` and `convert_pyi_to_ir` load the canonical
array subscription and `Annotated[...]` metadata into the same storage
contracts emitted by the Fortran semantic pipeline. Focused round-trip tests
cover:

```text
Fortran parser model -> semantic IR -> .pyi -> semantic IR
```

The loader rejects removed dimension helper syntax in type annotations. Use
array subscriptions such as `Float64[n]`, `Float64[:, :]` or
`Float64[::Strided]` instead.

## Deferred C Work

The shared model is capable of representing future C functions, variables,
fields, constants, scalar references, pointers, arrays with known contracts,
origin metadata, mutability and ownership facts. This task does not implement:

- `semantics/c2ir.py`;
- C semantic conversion;
- C `.pyi` generation;
- C wrapper lowering;
- C ownership, callback or pointer policy inference.

Future C conversion should use the same notation: by-value scalars as bare
types, unrefined pointers as `Ptr(T)` or `Ptr(Const(T))`, and array notation
only when a real array storage contract is known.
