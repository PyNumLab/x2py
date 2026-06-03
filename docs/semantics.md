# Semantic IR And `.pyi` Reference

This file is the single reference for semantic type names, C-to-IR conversion,
editable `.pyi` contracts, and the exact native C semantic stub rules. It is
kept together because parser frontends should converge on one semantic model
before wrapper generation makes language-specific lowering decisions.

## Datatype Mapping

This document records the shared scalar datatype policy used when C and Fortran
parser facts are converted to semantic IR. The semantic names are the stable
bridge between parser-native type spellings, `.pyi` output, readiness checks,
and eventual NumPy-oriented wrapper code.

### Semantic Names

| Semantic dtype | NumPy equivalent | Notes |
| --- | --- | --- |
| `Bool` | `numpy.bool_` | Boolean scalar. |
| `Int8`, `Int16`, `Int32`, `Int64` | `numpy.int8`, `numpy.int16`, `numpy.int32`, `numpy.int64` | Signed integers. |
| `UInt8`, `UInt16`, `UInt32`, `UInt64` | `numpy.uint8`, `numpy.uint16`, `numpy.uint32`, `numpy.uint64` | Unsigned integers. |
| `Float32`, `Float64` | `numpy.float32`, `numpy.float64` | Binary floating-point scalars. |
| `Float128` | `numpy.longdouble` | Platform precision varies; `numpy.float128` is not portable. |
| `Complex64`, `Complex128` | `numpy.complex64`, `numpy.complex128` | Complex scalars. |
| `Complex256` | `numpy.clongdouble` | Platform precision varies. |
| `String` | `numpy.str_` or byte storage at ABI boundary | Character policy depends on wrapper ABI. |
| `SizeT` | `numpy.uintp` | Target width is compiler-probed when available. |
| `Any` | `object` | Used for void pointer pointees and intentionally opaque values. |

### Fortran Intrinsics

| Fortran spelling or kind | Semantic dtype | NumPy equivalent |
| --- | --- | --- |
| `integer`, `integer(kind=4)`, `integer(int32)`, `integer(c_int)`, `integer(c_int32_t)` | `Int32` | `numpy.int32` |
| `integer(kind=1)`, `integer(int8)`, `integer(c_signed_char)`, `integer(c_int8_t)` | `Int8` | `numpy.int8` |
| `integer(kind=2)`, `integer(int16)`, `integer(c_short)`, `integer(c_int16_t)` | `Int16` | `numpy.int16` |
| `integer(kind=8)`, `integer(int64)`, `integer(c_long_long)`, `integer(c_int64_t)` | `Int64` | `numpy.int64` |
| `real`, `real(kind=8)`, `real(real64)`, `real(c_double)`, `real(kind(1.0d0))` | `Float64` | `numpy.float64` |
| `real(kind=4)`, `real(real32)`, `real(c_float)`, `real(kind(1.0e0))` | `Float32` | `numpy.float32` |
| `real(kind=16)`, `real(real128)`, `real(kind(1.0q0))` | `Float128` | `numpy.longdouble` |
| `complex`, `complex(kind=8)`, `complex(real64)`, `complex(c_double_complex)` | `Complex128` | `numpy.complex128` |
| `complex(kind=4)`, `complex(real32)`, `complex(c_float_complex)` | `Complex64` | `numpy.complex64` |
| `complex(kind=16)`, `complex(real128)` | `Complex256` | `numpy.clongdouble` |
| `logical`, `logical(kind=1/2/4/8)`, `logical(c_bool)` | `Bool` | `numpy.bool_` |
| `character`, `character(kind=1)`, `character(kind=c_char)` | `String` | `numpy.str_` or ABI byte storage |
| `procedure(...)` | `Procedure` | Callback/interface policy |

### C Types

| C spelling or parser type | Semantic dtype | NumPy equivalent |
| --- | --- | --- |
| `_Bool` / `CBool` | `Bool` | `numpy.bool_` |
| `char`, `signed char` | `Int8` | `numpy.int8` |
| `unsigned char` | `UInt8` | `numpy.uint8` |
| `short`, `unsigned short` | `Int16`, `UInt16` | `numpy.int16`, `numpy.uint16` |
| `int`, `unsigned int` | `Int32`, `UInt32` | `numpy.int32`, `numpy.uint32` |
| `long`, `long long` | `Int64` | `numpy.int64` |
| `unsigned long`, `unsigned long long` | `UInt64` | `numpy.uint64` |
| `float`, `double`, `long double` | `Float32`, `Float64`, `Float128` | `numpy.float32`, `numpy.float64`, `numpy.longdouble` |
| `float _Complex`, `double _Complex`, `long double _Complex` | `Complex64`, `Complex128`, `Complex256` | `numpy.complex64`, `numpy.complex128`, `numpy.clongdouble` |
| `int8_t`, `int16_t`, `int32_t`, `int64_t` | `Int8`, `Int16`, `Int32`, `Int64` | Matching signed NumPy integer |
| `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t` | `UInt8`, `UInt16`, `UInt32`, `UInt64` | Matching unsigned NumPy integer |
| `size_t` | `SizeT` or probed unsigned width | `numpy.uintp` or matching `numpy.uint*` |

C integer spellings such as `long` are ABI-dependent in general C, but the
current semantic policy maps parsed primitive `long` and `long long` to 64-bit
semantic dtypes. Standard-library typedefs are refined through the compiler
standard-type probe when facts are supplied.

## C To Semantic IR Mapping

Status: first C semantic conversion subset implemented in `semantics/c2ir.py`.
The converter consumes `c_parser` models and emits the same language-neutral
semantic IR used by Fortran and edited `.pyi` files. Shared primitive dtype
policy is documented in the datatype mapping section above.

### Supported Identity Subset

- C translation unit -> one `SemanticModule` named from the source file stem.
- C function -> `SemanticFunction`, preserving native name and parameter order.
- C parameter -> `SemanticArgument`.
- `void` return -> `None`.
- `_Bool` -> `Bool`.
- `char` -> `Int8` with `c_char_policy` metadata; `signed char` -> `Int8`;
  `unsigned char` -> `UInt8`.
- `short`, `int`, `long`, and `long long` map to fixed signed integer names
  using the current Linux-oriented defaults: `Int16`, `Int32`, `Int64`,
  `Int64`.
- Unsigned integer spellings map to `UInt16`, `UInt32`, `UInt64`, and
  `UInt64`; fixed-width typedef spellings such as `uint32_t` map to the
  matching `UInt*` fallback.
- `float` -> `Float32`; `double` -> `Float64`; `long double` -> `Float128`.
- `float _Complex` -> `Complex64`; `double _Complex` -> `Complex128`;
  `long double _Complex` -> `Complex256`.
- Local typedef chains are resolved when their parser model definitions are
  available.
- `size_t` maps to `SizeT` without a target probe; supplied
  `x2py.c_type_probe` facts override standard typedefs with width-specific
  `Int*`, `UInt*`, or `Float*` semantic names.
- Opaque standard-type probe facts such as `FILE` create named opaque semantic
  classes when referenced by converted declarations.
- Object-like numeric macros and enum constants become `Final`-style semantic
  variables through the `Constant` constraint.
- Struct definitions become `SemanticClass` entries. Incomplete structs become
  opaque classes and may be used through direct `Ptr(...)` identity contracts.
- Explicit multi-header conversion resolves a struct to the header that defines
  it. Other generated stubs import that owner class instead of emitting
  duplicate definitions.
- Structs originating from private included headers remain usable through
  generated owner-module `class Name(Opaque): pass` dependency stubs.
- Declared C arrays, including adjusted array parameters, become semantic array
  storage contracts with C order for rank greater than one.
- Pointers become explicit `SemanticStorageContract` pointer/reference
  metadata. `const` on the pointee makes the storage read-only, and `restrict`
  is preserved as aliasing metadata.

### Conservative Blockers

The converter does not silently invent wrapper policy. It attaches
`readiness_blockers` metadata that the semantic readiness checker reports:

- unresolved typedef or unknown type references;
- legacy parser reports carrying macro-dependent declarations;
- variadic functions;
- function pointer/callback signatures without edited `.pyi` `Callable`
  policy;
- mutable numeric or `void *` pointer parameters without ownership,
  scalar-reference, or array policy;
- arrays with unknown extents;
- incomplete or external opaque structs used by value;
- unions used in semantic signatures;
- `volatile`, `_Atomic`, bitfields, and unsupported declarator compositions.

The current C semantic path supports `--language c --semantics`,
`--language c --wrap-readiness`, and starter exact-contract
`--language c --pyi` output for this supported subset. Generated stubs remain
conservative: ambiguous ownership, callback, ABI-extension, and Pythonic
projection policy stays out of the generated `.pyi` until supplied by the
semantic model or an edited interface. In particular, an unresolved typedef is
not assumed to be opaque because its ABI representation is unknown.

## Wrapper `.pyi` Format

The semantic `.pyi` format is a Python-valid view of x2py semantic IR. It is
language-neutral: Fortran and future C inputs use the same type, storage,
pointer, array, layout and metadata notation. Source language differences are
represented by contracts and metadata, not by separate syntax families.

This document describes the behavior implemented for the current Fortran and C
semantic conversion paths.

### Canonical Type And Storage Contract

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
def assumed(x: Annotated[Float64[::Strided, ::Strided], ORDER_F]) -> None: ...
```

There is no separate dimension helper in canonical type syntax. A dimension
entry without colons is an extent (`Float64[n]`, `Float64[n, m]`). Slice-like
entries express range or stride contracts (`Float64[1:n]`,
`Float64[::Strided]`, `Float64[:, 0:n:m]`). `Strided` means the runtime stride
is part of the accepted storage contract.

Generic semantic constraints are not represented as type subscriptions.
Constants use `Final[T]`; other constraints and non-dimensional array metadata
use `Annotated[T[...], Constraint, ...]`.

`Annotated[...]` carries non-dimensional metadata:

- `ORDER_F` for a Fortran-oriented multidimensional contract.
- `ORDER_ANY` for an orientation-independent multidimensional strided
  contract chosen explicitly by an edited interface or later projection.
- `Allocatable` for a Fortran allocatable array.
- `Pointer` for a Fortran pointer array.
- `Intent("out")` when a visible exact-native argument has source intent
  `out`; `intent(inout)` is the default writable reference/array spelling and
  does not need metadata.

Plain multidimensional array notation is C-oriented (`ORDER_C`) by default.
Under the current Fortran generation policy, every multidimensional Fortran
array contract emits `ORDER_F`, including stride-aware assumed-shape arrays.
Rank-one storage has no C-versus-Fortran order distinction, so no order marker
is emitted for vectors.

`ArrayCategory(...)`, `SourceDims(...)`, `LowerBounds(...)` and `Contiguous`
are not part of newly generated canonical array annotations. They described
native declaration provenance rather than additional requirements on the
Python-visible array. The loader continues to accept existing edited stubs
that contain these metadata forms. Fortran source category, original bounds
and declaration dimensions may remain available as internal source provenance
when converting source; they are not required for the public storage contract
or for ordinary Python-to-Fortran array argument association.

### Implemented Fortran Exact Form

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

### Implemented Fortran Arrays

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

Assumed-size arrays preserve their fixed rank and any dimensions constrained by
the visible storage contract. A rank-one `x(*)` is emitted as `T[:]`; for
`x(n, *)`, the second dimension has an unconstrained runtime extent, not an
unknown rank:

```python
def legacy(values: Float64[:]) -> None: ...

def legacy_matrix(
    n: Ptr(Const(Int32)),
    a: Annotated[Float64[n, :], ORDER_F]
) -> None: ...
```

Assumed-shape arrays are stride-aware. A rank-one assumed-shape dummy is
emitted as a strided vector. Under the current generated-wrapper policy, a
rank-two or higher assumed-shape dummy retains Fortran orientation while
permitting strides:

```python
def vector(x: Float64[::Strided]) -> None: ...

def matrix(
    a: Annotated[
        Const(Float64[::Strided, ::Strided]),
        ORDER_F,
    ]
) -> None: ...
```

The Fortran declaration itself may permit an actual argument with another
orientation. The generated semantic interface deliberately chooses
Fortran-oriented storage by default. An edited interface or future projection
may choose `ORDER_ANY` only with corresponding backend and validation policy.
`contiguous` assumed-shape arrays use dense dimensions instead of
`::Strided`; their multidimensional forms also carry `ORDER_F`.

Explicit bounds are expressed through storage extents, not source-dimension
metadata. For example, `x(1:n)` has storage extent `n`; `x(0:n-1)` also has
extent `n` (the implementation currently retains the equivalent arithmetic
expression when it is not simplified). Python arrays present zero-based
storage; the compiled Fortran call associates that storage with the dummy
argument and supplies the lower and upper bounds declared by the procedure.
Those Fortran bounds affect indexing within the procedure, not what bound
metadata Python must pass. The public contract therefore needs the required
extent, layout and mutability, not `LowerBounds(...)`.

Allocatable and pointer arrays preserve their source storage property:

```python
class workspace:
    values: Annotated[Float64[:], Allocatable]

def section(
    x: Annotated[Float64[:], Pointer]
) -> None: ...
```

Allocation or association replacement policy is not implemented. The semantic
IR preserves the facts needed for readiness and lowering decisions; a backend
must not silently treat replacement-capable allocatable or pointer dummies as
ordinary borrowed arrays.

### Preserved Metadata

The shared semantic model separates:

- value type (`Float64`, `Int32`, derived type names);
- storage/calling contract (`value`, `reference`, `pointer`, `array`);
- public array contract (rank, required extents or admitted strides, order,
  contiguity, allocatable and pointer semantics);
- source origin metadata (source language, native name, native scope,
  source-level type/category information and lowering-relevant facts).

The Fortran converter currently preserves public storage dimensions, order,
`intent`, optionality, `value`, constants, `allocatable` and `pointer` in the
visible semantic contract. It retains source declaration dimensions, bounds,
dummy category and `contiguous` provenance internally where the parser
supplies those facts for diagnostics or native-interface provenance; those
facts do not add visible array requirements.

### Loading And Round Trips

`parse_pyi_text`, `load_pyi_file` and `convert_pyi_to_ir` load canonical
array subscriptions and `Annotated[...]` metadata into the same public
storage contracts emitted by the Fortran semantic pipeline. Native
source-provenance details not emitted into the public type are intentionally
excluded from public contract equality. Focused round-trip tests cover:

```text
Fortran parser model -> semantic IR -> .pyi -> semantic IR
```

The loader rejects removed dimension helper syntax in type annotations. Use
array subscriptions such as `Float64[n]`, `Float64[:, :]` or
`Float64[::Strided]` instead.

### Pythonic Projection (Later)

The implemented Fortran generator emits the exact form described above. A
later optional generation or editing mode, for example `--pythonic`, may
expose a friendlier Python API whose arguments or results differ from that
native contract. Such a projected interface must retain a mapping back to the
exact semantic/native interface; it must not discard source origin, storage,
intent, shape, ownership or lowering facts needed to issue the call.

A projection is allowed to be more restrictive or more expressive than the
exact native interface, according to the Python API the user wants to expose.
It may add accepted-input coercions, local constraints, cross-argument checks,
result checks, mutation policy or ownership policy. It need not expose every
use that the native routine could technically accept. At the native-call
boundary, however, the mapped native values must still satisfy the
requirements encoded by the exact native contract.

The Fortran converter does not automatically generate a projected interface.
The loader and printer retain explicit projection mappings for edited semantic
stubs, including `@native_call` entries formed from `Arg`, `Return`, `Const`,
`Len`, `IsPresent`, `Work` and `.shape[...]`, plus `Returns[...]`. The
pointer/reference adaptation examples below (`Ptr(Arg(...))` and
`Ptr(Return(...))`), `As[...]`, `.strides[...]`, coercion policy and
validation contracts describe extensions required for the fuller Pythonic
projection; they are not currently accepted or emitted by this path.

#### Native Argument Projection

Only a projected interface uses `@native_call`. The decorator records how
visible Python arguments and projected results supply the exact native
arguments.

For a mutable scalar reference, the implemented exact Fortran form keeps
caller-supplied storage:

```python
# Implemented exact form.
def advance(value: Ptr(Float64)) -> None: ...
```

A future Pythonic form may create writable temporary storage, perform the
native call and read the updated value back as a Python result:

```python
# Projected form, not currently implemented.
@native_call([Ptr(Arg(0))])
def advance(value: Float64) -> Returns["value", Float64]: ...
```

Similarly, an `intent(out)` scalar currently remains an explicit writable
reference with its preserved source intent:

```python
# Implemented exact form.
def get_count(result: Annotated[Ptr(Int32), Intent("out")]) -> None: ...

# Projected form, not currently implemented.
@native_call([Ptr(Return(0))])
def get_count() -> Int32: ...
```

A projection may derive hidden native metadata from a visible array. For a
future native interface with a by-value length parameter, for example:

```python
# Exact contract for a future supported native frontend.
def sum_values(n: SizeT, values: Const(Float64[n])) -> Float64: ...

# Projected form, not currently implemented.
@native_call([As[SizeT](Arg(0).shape[0]), Arg(0)])
def sum_values(values: Const(Float64[:])) -> Float64: ...
```

`Arg(i).shape[dim]` denotes a zero-based array extent.
`Arg(i).strides[dim]` denotes a NumPy byte stride:

```python
@native_call([Arg(0), Arg(0).shape[1], Arg(0).strides[1]])
def process_columns(values: Const(Float64[:, ::Strided])) -> None: ...
```

Dimension steps such as `::m` are expressed in elements; deriving a native
element stride from a byte stride must include the item-size conversion in
the native mapping.

#### Coercions And Constraints

A Pythonic projection may accept values that are not already in the exact
storage form, but only through explicit allowed coercions. For example, a
projected API could allow a NumPy C-order matrix to be copied into an
`ORDER_F` value required by a Fortran-oriented exact contract. It may instead
reject that input when no copying coercion is declared.

Coercions and constraints serve different purposes:

- A coercion states how an accepted Python object becomes the required
  semantic runtime value, potentially allocating storage or changing layout.
- A constraint states what must be true of the adapted value before native
  lowering, such as dtype, rank, shape, stride capability, `ORDER_F`,
  mutability, device residence, alignment or ownership.

The exact notation already records native-facing local constraints, including
`Ptr(Const(T))`, `Const(T[...])`, dimensions, `ORDER_F`, `ORDER_ANY`,
`Allocatable` and `Pointer`. A projected API may add allowed conversion
policy, for example a future `From(np.ndarray, copy=True)` spelling, but it
cannot silently weaken the exact native contract.

The exact native contract is therefore a minimum obligation for a projection.
A projected API may require additional properties, such as finite values,
non-aliasing arguments, a square matrix or a no-copy policy. A declared
coercion may convert a projected input so that it satisfies a native
requirement, such as packing C-oriented input into `ORDER_F` storage. But the
mapped value sent to native lowering must satisfy the encoded native element
type, reference/read-write contract, rank, extent, layout, stride,
allocation/association and other calling-relevant requirements.

This document does not currently define a hard-versus-soft classification for
exact-contract constraints. Until such a classification and override policy
exist, constraints encoded in the exact native interface are mandatory at the
native-call boundary. A later design may classify advisory requirements, such
as a preferred layout or zero-copy preference, as relaxable by an explicit
projection policy. ABI, memory-safety and semantic-correctness requirements
cannot be treated as advisory.

In particular, conversion and copy-back policies are required before a
projection can:

- accept C-order or non-contiguous storage for a target requiring dense
  Fortran-oriented storage;
- expose mutable scalar references as ordinary scalar inputs and returns;
- return changes to output arrays through allocated temporary storage;
- expose replacement-capable `Allocatable` or `Pointer` dummies; or
- preserve ownership, lifetime and aliasing behavior through a temporary.

#### Validation Contracts

Local constraints are not sufficient for relationships between multiple
arguments or for promises about projected results. A future projected
interface may add a validation contract, whether or not the exact native
interface already contains local constraints, for:

- preconditions, such as matching extents or non-aliasing inputs;
- postconditions, such as the returned shape or dtype;
- invariants on projected objects after mutation;
- mutation and aliasing rules; and
- ownership and lifetime rules for borrowed, owned, viewed or temporary
  storage.

For example, this is an illustrative later projected interface, not currently
accepted projection syntax:

```python
@contract(
    pre=[
        lambda ctx: ctx.args.a.shape[0] == ctx.args.a.shape[1],
        lambda ctx: ctx.args.b.shape == (ctx.args.a.shape[0],),
    ],
    post=[lambda ctx: ctx.result.shape == ctx.args.b.shape],
    invariants=[lambda ctx: not ctx.result.aliases(ctx.args.a)],
)
def solve(
    a: Annotated[Float64[:, :], ORDER_F],
    b: Float64[:],
) -> Float64[:]: ...
```

A constraint can require that `a` is `ORDER_F`; a contract can require that
`a` is square, that `b` agrees with its extent and that the result does not
alias mutable input storage. These checks occur at distinct levels and must
remain distinct in a later semantic model. Projection-level checks supplement
the exact native contract; they do not replace its mandatory native-call
checks.

A projected call therefore has the following conceptual sequence:

```text
visible Python values
  -> projected allowed coercions
  -> projected local constraints and contract preconditions
  -> exact native argument mapping
  -> mandatory exact-native constraint validation
  -> backend lowering
  -> native call
  -> contract postconditions and invariants
  -> projected Python results
```

The projection mechanism is language-neutral. It can later adapt exact
Fortran or C contracts through the same notation and runtime concepts, but
this milestone does not implement automatic Pythonic generation, current
exact-reference adaptation, coercion/contract execution or C wrapper lowering.
The C frontend can generate starter exact-contract `.pyi` output for the
implemented semantic subset.

### External Opaque Type Stubs

An external source-language type whose owner module is not part of the explicit
wrapping target is emitted as an owner-module opaque dependency stub. This
applies to imported Fortran derived types and to C opaque structs from external
header surfaces:

```python
# types_mod.pyi
class particle(Opaque):
    pass
```

The importing module references that owner rather than re-exporting the type:

```python
# physics.pyi
from types_mod import particle

def move(p: Ptr(particle)) -> None: ...
```

`emit_module_stubs(...)` produces the complete stub mapping. `load_pyi_modules`
loads one or more files or directories and reconciles those imports back into
semantic `external_type_ref` metadata. If the user replaces the opaque owner
stub with a concrete class body, the imported semantic reference becomes
`representation="wrapped"` without changing the importing stub.

This file-set round-trip is the editing boundary for future wrapper policy.
Existing type constraints encoded with `Annotated[...]` are preserved now.
Additional coercion and executable contract syntax remains deferred.

For C, an unresolved typedef is not automatically opaque: its ABI could be an
integer, pointer, struct, or another representation. The C frontend emits an
opaque class when declarations establish that contract, such as a forward
struct declaration or a private included struct used through pointers. An
edited `.pyi` file may also state the policy explicitly with `class
Name(Opaque): pass`.

### Deferred C Work

The shared model represents the current C semantic conversion subset for
functions, variables,
fields, constants, scalar references, pointers, arrays with known contracts,
origin metadata, mutability and ownership facts. The C frontend can generate
starter exact-contract stubs from that model. Remaining C work includes:

- C wrapper lowering;
- C ownership, callback or pointer policy inference beyond facts already
  present in exact contracts.

Future C conversion should use the same notation: by-value scalars as bare
types, unrefined pointers as `Ptr(T)` or `Ptr(Const(T))`, and array notation
only when a real array storage contract is known.

## Self-Contained C Semantic `.pyi` Contract

**Status:** Phase 1 implementation baseline
**Target:** Python wrappers for C libraries on a selected Linux ABI
**Primary requirement:** A semantic `.pyi` file plus a compiled library is
sufficient to generate a wrapper. C header parsing is optional input
generation, not a wrapper-generation dependency.

### 1. Phase 1 Boundary

Phase 1 implements the exact callable interface first. Python is intentionally
C-like at this stage:

- Every visible Python argument corresponds to one native C parameter, in the
  same order.
- Every direct Python return annotation corresponds to the direct C return.
- Native `void` is written as `None`.
- Native pointer parameters are supplied by the Python caller as pointer-backed
  storage, primarily NumPy zero-dimensional storage or NumPy arrays.
- Output pointer parameters remain input arguments: the caller allocates
  mutable storage and observes changes after the call.
- No argument is synthesized, reordered, omitted or converted into a Python
  result by the wrapper.

Therefore, Phase 1 does **not** implement or emit `@native_call`.

The purpose of this ordering is to prove that x2py can describe, parse, lower
and execute direct C signatures reliably before adding Pythonic adaptations.

### 2. Non-Negotiable Rules

1. The semantic `.pyi` must be sufficient to call every supported wrapped
   symbol without reading C source at build time.
2. Optional C parsing may generate a starter semantic `.pyi`, but generated
   wrappers consume only the semantic `.pyi` and the compiled library.
3. Phase 1 functions use identity parameter mapping only: one Python argument
   per C parameter, in native order.
4. Phase 1 returns use identity return mapping only: the Python return is the
   direct C return, or `None` for native `void`.
5. A C pointer parameter is never silently represented by a plain immutable
   Python scalar. The caller supplies pointer-backed storage.
6. A bare numeric pointer uses `Ptr(T)` for writable storage and
   `Ptr(Const(T))` for read-only storage. For an API known to use that pointer
   as a scalar reference, callers conventionally pass matching
   zero-dimensional NumPy storage. Numeric pointer parameters with a recorded
   array shape contract use `T[dimension-specs]` or `T[...]`. All these
   one-level storage forms lower to one native pointer; C does not carry
   rank, shape or stride metadata in an ordinary `T *` parameter.
7. Array dimensions express validation constraints, not additional pointer
   depth. `Float64[:, :]` still lowers to one `double *`, never `double **`.
8. With no stride or order modifier, numeric array storage in a C-origin
   semantic stub is implicitly C-contiguous. Generated C stubs omit redundant
   `ORDER_C`.
   Rank-one contiguous storage has no C-versus-Fortran order distinction, so
   `T[:]` and `T[n]` never need `ORDER_F` either. A non-contiguous vector uses
   stride notation such as `T[::Strided]`, not an order modifier.
   For multidimensional storage, order and stride constraints are independent.
   `ORDER_C` is not needed in canonical stubs because bare array notation,
   including `T[::Strided, ::Strided]`, already carries the C orientation.
   The explicit non-default layout form is
   `Annotated[T[dimension-specs], ORDER_F]`, including
   `Annotated[T[::Strided, ::Strided], ORDER_F]` for a Fortran-oriented
   strided contract. `ORDER_ANY` represents a multidimensional strided
   contract with no C/F orientation restriction.
   A stride-aware axis is written `::Strided`, as in
   `Float64[:, ::Strided]` or `Float64[:, 0:n:Strided]`. It is a direct
   interface when any native extent or stride values remain visible arguments;
   the exact interface must not generate them.
9. `Const(...)` is the canonical spelling for a read-only C pointee/storage
   contract.
10. Pointer graphs such as `T **` and deeper are not inferred from NumPy
    arrays. They are represented directly as `Ptr[n](T)` and require the
    caller to supply a compatible low-level native pointer object.
11. Functions requiring hidden outputs, generated lengths, Python string
    conversion, handle conversion, callback thunks, status-to-exception
    conversion, packing or copy-back are deferred until after identity calls
    work.
12. The current target is a selected Linux ABI. Cross-platform variation and
    non-default calling conventions are deferred.

### 3. Current Artifact

The current compiler-facing artifact is:

```text
module.x2py.pyi
```

It may use x2py semantic types, but it contains only identity-callable
functions in Phase 1.

A clean `.pyi` for standard type checkers is not part of Phase 1.

### 4. Scalar Types Passed By Value

Bare scalar types represent native by-value parameters and direct native
returns.

| Semantic type | C interpretation on selected target |
| --- | --- |
| `Int` | ordinary C `int` |
| `Int8`, `Int16`, `Int32`, `Int64` | fixed-width signed integer types |
| `UInt8`, `UInt16`, `UInt32`, `UInt64` | fixed-width unsigned integer types |
| `Float32` | `float` |
| `Float64` | `double` |
| `SizeT` | `size_t` |
| `CLong`, `CULong` | C `long`, `unsigned long` |
| `Bool` | selected C boolean ABI type |

Example:

```c
int add(int a, int b);
double multiply(double a, double b);
```

```python
def add(a: Int, b: Int) -> Int: ...
def multiply(a: Float64, b: Float64) -> Float64: ...
```

No decorator is needed or accepted for these identity calls.

### 5. Numeric Pointer Storage

#### 5.1 Canonical Reference And Array Notation

A numeric NumPy storage annotation means the caller supplies memory whose data
address is passed directly to C. C ordinary pointer parameters contain no
rank, extent or stride descriptor. Therefore a native `double *values` with no
additional array contract is represented exactly as `Ptr(Float64)`;
dimensioned forms are used only when the C declaration, documented API
contract, or completed semantic stub provides those constraints.
A generated Fortran intermediary that prepares Fortran dummy arguments is a
Fortran backend concern and does not change the direct C `T *` contract
described in this document.

| Semantic annotation | Python caller supplies | Native parameter |
| --- | --- | --- |
| `Ptr(T)` | compatible writable native pointer-backed storage; a zero-dimensional NumPy array is the scalar-reference convention | `T *` |
| `Ptr(Const(T))` | compatible native pointer-backed storage under a read-only pointee contract | `const T *` |
| `Int[:]` | writable contiguous rank-one NumPy array; C/F order is equivalent | `int *` |
| `Const(Int[:])` | read-only contiguous rank-one NumPy array; C/F order is equivalent | `const int *` |
| `Float64[:]` | writable contiguous rank-one NumPy array; C/F order is equivalent | `double *` |
| `Const(Float64[:])` | read-only contiguous rank-one NumPy array; C/F order is equivalent | `const double *` |
| `Float64[n]` | writable one-dimensional array whose size is validated against visible argument or semantic constant `n` | `double *` |
| `Const(Float64[n])` | read-only one-dimensional array whose size is validated against visible argument or semantic constant `n` | `const double *` |
| `Float64[0:n]` | writable one-dimensional array with explicit half-open range `0:n` | `double *` |
| `Float64[:, :]` | writable rank-two C-contiguous NumPy array | `double *` |
| `Float64[3, 4]` | writable C-contiguous NumPy array with exact shape `(3, 4)` | `double *` |
| `Float64[...]` | writable C-contiguous NumPy array of any rank | `double *` |
| `Float64[...][1:4]` | writable C-contiguous NumPy array with rank 1, 2, or 3 | `double *` |
| `Float64[...][1, 2, 5]` | writable C-contiguous NumPy array with rank 1, 2, or 5 | `double *` |

`Float64[...]` means any rank (any number of dimensions). A following rank
selector restricts that set: `Float64[...][1:4]` accepts ranks 1 through 3
because the stop value is exclusive, while `Float64[...][1, 2, 5]` accepts
only ranks 1, 2, and 5. The same forms apply to other numeric element types
and inside `Const(...)`.

An axis entry without colons is an extent. `Float64[n]` means a rank-one
array of size `n`, and `Float64[n, m]` means an array with shape `(n, m)`;
neither denotes element indexing. A slice entry such as `Float64[0:n]`
expresses an explicit NumPy-style half-open range. It has the same size as
`Float64[n]` in this simple zero-based case, but retains range semantics for
forms with a lower bound or step.

`Ptr(T)` and `Ptr(Const(T))` preserve an unrefined one-level C pointer. For a
known primitive scalar-reference API, the canonical NumPy value is a
zero-dimensional array, as shown below. `T[dimension-specs]` and `T[...]`
with an optional rank selector are NumPy-backed array-pointer spellings once
an array contract is known. A shape-bearing array annotation already
represents pointer-backed array storage; do not additionally wrap it in
`Ptr(...)`.

For multidimensional storage, order is orthogonal to rank, dimensions and
stride capability. `Annotated[Float64[:, :], ORDER_F]` denotes a rank-two
dense Fortran-contiguous array, while
`Annotated[Float64[::Strided, ::Strided], ORDER_F]` denotes a rank-two
Fortran-oriented strided array. Bare `Float64[::Strided, ::Strided]` retains
the default `ORDER_C` orientation, and
`Annotated[Float64[::Strided, ::Strided], ORDER_ANY]` imposes no C/F
orientation restriction. `Annotated[Float64[...][1:4], ORDER_F]` expresses
the corresponding Fortran-oriented rank-polymorphic contract. These spellings
define the semantic format; they are explicit because `ORDER_F` and
`ORDER_ANY` are non-default in a C-origin stub. Accepting either in a
runnable C Phase 1 wrapper requires the corresponding native routine to
accept that storage layout directly. For a rank-one array, `ORDER_C` and
`ORDER_F` do not distinguish storage, contiguous or strided, so no order
constraint is written.
For a multidimensional strided annotation, `ORDER_F` is orientation metadata,
not a requirement that NumPy report `F_CONTIGUOUS`; non-unit strides remain
part of the contract.
Source frontends may retain original declaration dimensions, source bounds or
native dummy categories as internal provenance. Those source facts are not part
of the canonical public array annotation unless they produce an actual storage
constraint. In particular, Fortran dummy bounds are established by native
association rather than supplied as Python array metadata. The implemented C
conversion subset is described in the C-to-semantic IR mapping section above.

Stride-aware dimensions use a slice step marker:

| Semantic annotation | Meaning | Exact-call condition |
| --- | --- | --- |
| `Float64[::Strided]` | Rank-one array with a runtime element stride. | Any required stride argument is separately visible in the native signature. |
| `Float64[:, ::Strided]` | Rank-two array whose second axis has runtime stride metadata. | Any required stride argument is separately visible in the native signature. |
| `Float64[::Strided, ::Strided]` | Rank-two strided array with implicit `ORDER_C` orientation. | Any required stride arguments are separately visible in the native signature. |
| `Annotated[Float64[::Strided, ::Strided], ORDER_F]` | Rank-two strided array with required Fortran orientation. | The native routine accepts that orientation and any required stride arguments remain visible. |
| `Annotated[Float64[::Strided, ::Strided], ORDER_ANY]` | Rank-two strided array with no C/F orientation restriction. | The native routine accepts arbitrary orientation and any required stride arguments remain visible. |
| `Float64[:, ::2]` | Rank-two array whose second-axis element step is exactly two. | The native routine consumes that layout directly. |
| `Float64[:, 0:n:Strided]` | Rank-two array with bounded second axis and an arbitrary runtime step. | `n` and any required stride metadata are native inputs. |
| `Float64[:, 0:n:m]` | Rank-two array with bounded second axis and exact symbolic step `m`. | `n` and `m` are native inputs or semantic constants. |

`Float64[:, ::]` does not select a strided representation: under Python slice
semantics it is just `Float64[:, :]`. A stride-aware array cannot be passed
correctly to an operation that assumes contiguous storage unless the native
call also receives required strides or the wrapper performs an explicit
packing/copy-back conversion.

Slice dimensions follow `lower:upper:step`. A literal bound or step is checked
directly. A symbolic bound or step, such as `n` or `m` in
`Float64[:, 0:n:m]`, must resolve from a visible scalar parameter or a
declared semantic constant such as `Final[Int]`. A later wrapper projection
may derive native metadata from array storage using NumPy notation, for
example `Arg(0).shape[1]` or `Arg(0).strides[1]` in a later Pythonic view,
but the exact interface does not synthesize such arguments. Resolvable
arithmetic expressions such as `2*n`
can be added later without requiring a new dimension notation. Annotation
steps use NumPy element units, while `Arg(0).strides[1]` has NumPy's byte
units; converting between them is an explicit later mapping decision.

#### 5.2 Pointer Depth And Opaque Pointers

`Ptr(...)` expresses native pointer depth directly. For a one-level pointer,
it preserves the native address form without inventing rank or shape. A known
primitive scalar-reference use may be supplied with zero-dimensional NumPy
storage. For an opaque argument or a direct pointer return, it represents a
typed low-level native pointer object:

| Semantic annotation | Native parameter |
| --- | --- |
| `Ptr(T)` | `T *`; writable unrefined one-level pointer storage |
| `Ptr(Const(T))` | `const T *`; read-only unrefined one-level pointer storage |
| `Ptr[2](T)` | `T **` direct low-level pointer object |
| `Ptr[2](Const(T))` | `const T **` direct low-level pointer object |
| `Ptr[n](T)` | `T` followed by exactly `n` native pointer layers, `n >= 2` |

`Ptr(x)` is the only canonical depth-one spelling. `Ptr[1](x)` is invalid.

For array storage whose dimensions are known, use an array form such as
`Int[n]` or `Float64[:, :]` rather than `Ptr(Int)` or `Ptr(Float64)`. When
the only available C fact is a data pointer with no rank or extent contract,
retain `Ptr(T)`. `Ptr[n](T)` is necessary for pointer graphs and for low-level
pointer values that are not represented by a shaped NumPy storage contract.

A direct pointer object carries a typed native address. Passing or returning
it does not imply allocation, copying, ownership or automatic destruction.
For example, a raw pointer returned by one native function can be passed to a
second native function under matching `Ptr(...)` annotations. Pointer-object
construction/allocation helpers are runtime API work, not additional
information required in a semantic function signature.

#### 5.3 Pointer To Scalar

```c
void increment(int *value);
void read_count(const int *value);
```

Phase 1 interface:

```python
def increment(value: Ptr(Int)) -> None: ...
def read_count(value: Ptr(Const(Int))) -> None: ...
```

Python use is intentionally storage-oriented:

```python
value = np.empty((), dtype=np.intc)
value[...] = 7
increment(value)
updated = value.item()
```

The wrapper passes `value`'s data address. It does not construct temporary
scalar storage and does not return the mutation.

#### 5.4 Pointer To Array

```c
void negate(int n, double *values);
double sum_values(size_t n, const double *values);
```

Phase 1 interface:

```python
def negate(n: Int, values: Float64[n]) -> None: ...
def sum_values(n: SizeT, values: Const(Float64[n])) -> Float64: ...
```

The caller supplies `n` explicitly because it is an actual C parameter. The
wrapper must not derive it from `len(values)` in Phase 1.

#### 5.5 Output Pointer Remains An Argument

```c
void get_count(int *out);
void get_values(int n, double *out);
```

Phase 1 interface:

```python
def get_count(out: Ptr(Int)) -> None: ...
def get_values(n: Int, out: Float64[n]) -> None: ...
```

Example Python use:

```python
out_count = np.empty((), dtype=np.intc)
get_count(out_count)
count = out_count.item()

out_values = np.empty(n, dtype=np.float64)
get_values(n, out_values)
```

Returning `Int` from `get_count()` or allocating and returning
`Float64[n]` from `get_values(n)` is a later Pythonic adaptation, not an
identity call.

### 6. Array Constraints

#### 6.1 Rank, Accepted Ranks And Fixed Dimensions

Dimensions refine valid NumPy storage while the native argument remains one
data pointer. They are semantic/API contracts rather than metadata transported
by a C `T *`. A bare pointer imported without such a contract remains raw:

```c
void process_raw(double *values);
```

```python
def process_raw(values: Ptr(Float64)) -> None: ...
```

Once the semantic interface records valid array contracts, it may use:

```c
void process_matrix(double *matrix);
void process_any(double *values);
void process_vector_or_matrix(double *values);
void use_row(int (*row)[4]);
void use_matrix(int (*matrix)[4]);
```

```python
def process_matrix(matrix: Float64[:, :]) -> None: ...
def process_any(values: Float64[...]) -> None: ...
def process_vector_or_matrix(values: Float64[...][1, 2]) -> None: ...
def use_row(row: Int[4]) -> None: ...
def use_matrix(matrix: Int[:, 4]) -> None: ...
```

- `Float64[:, :]` validates rank two and C contiguity, then passes one
  `double *`.
- `Float64[...]` accepts any rank and passes one `double *`.
- `Float64[...][1, 2]` accepts rank one or rank two and passes one
  `double *`.
- `Int[4]` validates one fixed row of four `int` values, then passes one
  address.
- `Int[:, 4]` validates contiguous rows of fixed width four, then passes one
  address.

For function parameters on the selected ABI, `int (*)[4]` is represented as
one pointer plus its fixed row-width contract. It is not represented as
`int **`.

#### 6.2 Strided Direct Interfaces Keep Native Metadata Visible

The semantic notation can distinguish a stride-aware view from a contiguous
matrix while retaining the exact native parameter list:

```c
void process_bounded_step(int n, int m, double *values);
void process_columns(const double *values, size_t columns, size_t stride_bytes);
```

```python
def process_bounded_step(n: Int, m: Int, values: Float64[:, 0:n:m]) -> None: ...
def process_columns(
    values: Const(Float64[:, ::Strided]),
    columns: SizeT,
    stride_bytes: SizeT,
) -> None: ...
```

`Strided` means the axis stride must be carried or checked rather than assumed
to be contiguous. `::2` is the fixed-step equivalent. `0:n:m` validates a
bounded axis and exact element step using visible native values or declared
semantic constants. In `process_columns`, the caller supplies both the array
storage and its native `stride_bytes` argument; nothing is hidden or
generated. For a multidimensional array, a stride form may be combined with
`ORDER_F`, or with `ORDER_ANY` when no orientation is part of the native
contract; leaving it unannotated retains `ORDER_C`. A later Pythonic view may
hide that argument with
`Arg(0).strides[1]`, or request `Pack` / `CopyBack`.

#### 6.3 Pointer Graphs Are Different

```c
void use_rows(int **rows);
void update_value(int *****value);
```

Neither declaration is represented by `Int[:, :]`. NumPy array notation
supplies one array data address, optionally accompanied by native
extent/stride values; it does not create a pointer graph. Their exact
low-level Phase 1 interfaces are:

```python
def use_rows(rows: Ptr[2](Int)) -> None: ...
def update_value(value: Ptr[5](Int)) -> None: ...
```

The caller supplies an x2py-compatible native pointer object with the declared
topology. The wrapper passes it unchanged. Constructing pointer rows from
nested Python sequences and exposing `update_value(value: Int) -> Int` are
later Pythonic adaptations.

#### 6.4 Contiguity

Without an explicit layout or stride form, array annotations such as `T[:]`,
`T[:, :]`, `T[n]`, and `T[...]` require C-contiguous numeric storage; a
generated C stub does not repeat this as `ORDER_C`. Explicit non-default
forms such as `Annotated[T[:, :], ORDER_F]`,
`Annotated[T[::Strided, ::Strided], ORDER_F]`, or
`Annotated[T[::Strided, ::Strided], ORDER_ANY]` are exact interfaces when
the native routine accepts that layout and all required metadata remains
visible in the signature. A bare multidimensional stride form such as
`T[:, ::Strided]` is also exact when native metadata is visible, but retains
the implicit `ORDER_C` orientation. Automatic packing, copy-back, or
derivation of native metadata is a later Pythonic transformation.
For rank one, `T[:]` and `T[n]` are also the canonical Fortran-contiguous
spelling; write `T[::Strided]` when contiguity is not required.

### 7. Direct Native Returns

#### 7.1 Scalars And `void`

Direct scalar returns and native `void` are identity behavior:

```c
int status(void);
void reset(void);
```

```python
def status() -> Int: ...
def reset() -> None: ...
```

An integer return remains an integer return in Phase 1. It is not
automatically converted to an exception.

#### 7.2 Pointer Returns

A direct returned native pointer can be exposed as a low-level pointer object
without changing the C return topology:

```c
double *raw_values(void);
struct context *context_current(void);
```

```python
class context(Opaque):
    pass

def raw_values() -> Ptr(Float64): ...
def context_current() -> Ptr(context): ...
```

If a returned pointer is exposed immediately as NumPy storage, shape and
lifetime information is required. This also remains identity mapping because
the C function directly returns the represented pointer:

```c
double *create_values(int n);
void free_values(double *values);
```

```python
def create_values(n: Int) -> Annotated[
    Float64[n],
    Owned,
    FreeWith("free_values"),
]: ...
```

This does not require `@native_call` because the C function directly returns
the pointer represented by the Python return annotation. Until shape and
lifetime handling are implemented, return it as the corresponding direct
low-level pointer object or reject the higher-level NumPy view rather than
guessing.

### 8. Symbol Names

Argument and return identity is independent of symbol naming. Phase 1
supports `@bind` without introducing `@native_call`:

```c
int library_add(int a, int b);
void c_increment(int *value);
```

```python
@bind("library_add")
def add(a: Int, b: Int) -> Int: ...

@bind("c_increment")
def increment(value: Ptr(Int)) -> None: ...
```

`@bind` changes only which exported symbol is loaded. It does not synthesize
arguments, change pointers or alter results.

### 9. Structures, Enums And Non-Numeric Pointers

By-value enums and by-value structures can be Phase 1 identity interfaces once
their native representation and layout are complete in the semantic `.pyi`:

```c
struct point { double x; double y; };
struct point scale_point(struct point p, double factor);
```

```python
class point(Structure):
    x: Float64
    y: Float64

def scale_point(p: point, factor: Float64) -> point: ...
```

Opaque pointers may be represented directly without creating a Pythonic handle
API:

```c
struct context;
struct context *context_create(void);
void context_destroy(struct context *ctx);
int context_run(struct context *ctx);
```

```python
class context(Opaque):
    pass

def context_create() -> Ptr(context): ...
def context_destroy(ctx: Ptr(context)) -> None: ...
def context_run(ctx: Ptr(context)) -> Int: ...
```

This is C-like identity behavior: Python receives and passes the native pointer
object. Automatic ownership, destruction, status checking and output-handle
conversion are later policies.

The following remain outside the first identity subset unless their direct
native representations are implemented explicitly:

- Python `str` conversion for `char *` or `const char *` (raw byte/character
  storage may be represented directly);
- Python callables converted into native function pointers (a pre-existing
  low-level native function pointer may later be an identity argument);
- unions;
- variadic functions;
- `void *` beyond an explicitly selected raw/byte-storage representation.

### 10. Phase 1 Unsupported Transformations

Phase 1 must reject, or leave unresolved during optional C import generation,
any interface that requires the wrapper to change the native function shape.

Unsupported now:

| Desired behavior | Example C shape | Later mechanism |
| --- | --- | --- |
| Pass a Python scalar through a native pointer | `void increment(int *value)` exposed as `value = increment(value)` | `@native_call([Ptr(Arg(0))])` plus readback |
| Generate a hidden length | `double sum(size_t n, const double *x)` exposed as `sum(x)` | `Arg(0).shape[0]` in `@native_call` |
| Turn an output pointer into a Python result | `void get_count(int *out)` exposed as `get_count() -> Int` | `Ptr(Return(...))` in `@native_call` |
| Convert native status to exception | `int create(...);` with hidden status | `Status[...]` and `Check(...)` |
| Wrap a raw opaque pointer with ownership behavior | `struct ctx *` / `struct ctx **` | handle and lifetime policy |
| Convert Python strings to C strings | `const char *` from `str` | text encoding/termination policy |
| Generate callback thunks | function-pointer argument | callback lifetime/exception policy |
| Pack or copy a layout the native function does not accept | pointer to accepted native storage | `Pack` / `CopyBack` coercions |

The later syntax is retained as design direction only. It is not required by
the Phase 1 parser, IR, printer or wrapper generator.

### 11. Required Phase 1 Readiness Errors

The wrapper generator or optional importer must report unsupported behavior
instead of silently changing the interface.

| Code | Condition |
| --- | --- |
| `c_non_identity_call_unsupported` | A declaration or semantic interface requires synthesized, omitted, reordered or transformed parameters/results. |
| `c_pointer_object_mismatch` | A `Ptr(T)` argument lacks compatible native pointer-backed storage, or a multi-level pointer argument lacks the declared native pointer topology. |
| `c_numpy_pointer_return_policy_required` | A native pointer return is exposed as a shaped NumPy result without implemented lifetime handling or explicit required metadata; a direct raw `Ptr(T)` return remains identity behavior. |
| `c_numpy_dtype_mismatch` | Supplied NumPy storage does not have the exact semantic native element dtype. |
| `c_numpy_rank_mismatch` | Supplied NumPy storage does not satisfy declared rank or fixed-shape constraints. |
| `c_numpy_contiguity_required` | An unqualified dense C-contiguous array annotation receives non-contiguous storage. |
| `c_numpy_stride_mapping_required` | A Pythonic interface hides native stride parameters required for stride-aware storage without an explicit mapping such as `Arg(0).strides[1]`. |
| `c_numpy_writeability_required` | A mutable native pointer receives read-only NumPy storage. |
| `c_opaque_handle_conversion_unsupported` | A raw opaque pointer is requested as an owning/high-level Python handle rather than direct `Ptr(context)` identity. |
| `c_string_conversion_unsupported` | A Python string conversion is requested. |
| `c_callback_unsupported` | A Python callback-to-native-function-pointer mapping is requested. |
| `c_union_unsupported` | A callable interface includes an unsupported union. |
| `c_variadic_function_unsupported` | A variadic native function is requested. |
| `c_calling_convention_unsupported` | A non-default calling convention is required. |

### 12. Phase 1 Parser And Wrapper Requirements

The Phase 1 implementation must:

1. Parse scalar annotations and direct `None`/scalar return annotations.
2. Parse unrefined one-level pointer forms `Ptr(T)` and `Ptr(Const(T))`, and
   accept matching pointer-backed storage; known scalar-reference uses must
   support the zero-dimensional NumPy convention.
3. Parse numeric array storage forms: `T[:]`, `Const(T[:])`, `T[:, :]`,
   fixed or symbolic extents such as `T[3, 4]` and `T[n]`, explicit dependent
   ranges or steps such as `T[0:n]` and `T[:, 0:n:m]`, and rank-polymorphic
   forms such as `T[...]`, `T[...][1:4]`, and `T[...][1, 2, 5]`.
4. Lower each supported one-level scalar-reference or array-storage
   annotation to exactly one native pointer of its leaf type.
5. Parse and lower direct pointer forms `Ptr[n](T)` as exactly `n` native
   pointer layers, accepting compatible low-level native pointer objects at
   runtime.
6. Validate NumPy dtype, rank, fixed dimensions, explicit layout/stride
   constraints including `ORDER_F` and `ORDER_ANY`, and writeability before
   calling native code.
7. Preserve the visible parameter order exactly, including visible native
   count or stride parameters.
8. Preserve direct native scalar, pointer and native `void` returns.
9. Parse and apply `@bind("symbol")` for identity symbol renaming.
10. Parse complete by-value `Structure`, `Enum[T]` and opaque pointer leaf
   declarations if those existing declaration features are already runnable;
   otherwise report them as not yet supported without approximating them.
11. Reject `@native_call`, `Arg`, `Return`, `Returns`, `Status`, `Check`,
   `Pack`, `CopyBack` and callback conversion constructs as later-phase
   syntax if encountered in a Phase 1 runnable input.
12. Accept stride-aware direct interfaces only when any required native count
    or stride arguments remain visible; deriving them from array metadata is a
    later Pythonic mapping.
13. Never consult C source after a supported semantic `.pyi` has been parsed.

### 13. Phase 1 Tests

#### 13.1 By-Value Scalar Identity

```c
int add(int a, int b);
```

```python
def add(a: Int, b: Int) -> Int: ...
```

The wrapper passes two native `int` values and returns one native `int`.

#### 13.2 Mutable Scalar Pointer Storage

```c
void increment(int *value);
```

```python
def increment(value: Ptr(Int)) -> None: ...
```

Tests must verify that a writable zero-dimensional NumPy array is passed by
data address and that native mutation is observed after the call. A plain
Python `int` must be rejected for this signature.

#### 13.3 Read-Only Scalar Pointer Storage

```c
void read_count(const int *value);
```

```python
def read_count(value: Ptr(Const(Int))) -> None: ...
```

Tests must verify matching scalar storage/input acceptance and exact native
pointer lowering without writable requirements.

#### 13.4 Array Pointer With Explicit Count

```c
double sum_values(size_t n, const double *values);
```

```python
def sum_values(n: SizeT, values: Const(Float64[n])) -> Float64: ...
```

Tests must verify that the caller passes `n`, that the wrapper passes it
unchanged, and that no hidden `len(values)` argument is generated.

#### 13.5 Explicit Output Storage

```c
void get_count(int *out);
void get_values(int n, double *out);
```

```python
def get_count(out: Ptr(Int)) -> None: ...
def get_values(n: Int, out: Float64[n]) -> None: ...
```

Tests must verify mutation of caller-allocated output storage and that the
functions return `None`.

#### 13.6 Matrices And Pointer-To-Fixed-Array

```c
void matrix_data(double *matrix);
void matrix_rows(int (*matrix)[4]);
```

```python
def matrix_data(matrix: Float64[:, :]) -> None: ...
def array_data(values: Float64[...]) -> None: ...
def vector_matrix_or_rank5(values: Float64[...][1, 2, 5]) -> None: ...
def matrix_rows(matrix: Int[:, 4]) -> None: ...
```

Tests must verify one native pointer argument for each function, rank/shape
validation, and rejection of a representation treating either argument as
`T **`.

#### 13.7 Direct Pointer Graph Identity

```c
void use_rows(int **rows);
void update_value(int *****value);
```

```python
def use_rows(rows: Ptr[2](Int)) -> None: ...
def update_value(value: Ptr[5](Int)) -> None: ...
```

Tests must verify exact pointer depth in the parsed ABI contract and that
these arguments accept only matching direct low-level pointer objects. They
must not accept `Int[:, :]` or add any `@native_call` transformation.

#### 13.8 Raw Opaque Pointer Identity

```c
struct context;
struct context *context_create(void);
void context_destroy(struct context *ctx);
```

```python
class context(Opaque):
    pass

def context_create() -> Ptr(context): ...
def context_destroy(ctx: Ptr(context)) -> None: ...
```

Tests must verify that the returned raw native pointer object is accepted by
`context_destroy` without handle wrapping, ownership inference or
`@native_call`.

#### 13.9 Symbol Binding Without Transformation

```c
int library_add(int a, int b);
```

```python
@bind("library_add")
def add(a: Int, b: Int) -> Int: ...
```

Tests must verify that `@bind` changes symbol lookup only and leaves
argument/return lowering unchanged.

#### 13.10 Transformation Is Not Phase 1

The Phase 1 parser or readiness checker must reject a runnable interface using
later transformation syntax such as:

```python
@native_call([Ptr(Arg(0))])
def increment(value: Int) -> Returns["value", Int]: ...
```

The supported Phase 1 spelling for the same C function is:

```python
def increment(value: Ptr(Int)) -> None: ...
```

### 14. Phase 2: Pythonic Adaptations After Identity Works

After Phase 1 can call direct signatures reliably, an optional Pythonic
generation mode can use `@native_call` to expose APIs that differ from their
C parameter lists. The settled design direction is:

```python
# C: void increment(int *value);
@native_call([Ptr(Arg(0))])
def increment_value(value: Int) -> Returns["value", Int]: ...

# C: void get_count(int *out);
@native_call([Ptr(Return(0))])
def get_count() -> Int: ...

# C: double sum_values(size_t n, const double *values);
@native_call([As[SizeT](Arg(0).shape[0]), Arg(0)])
def sum_values(values: Const(Float64[:])) -> Float64: ...

# C: void process_columns(const double *values, size_t n, ptrdiff_t stride_bytes);
@native_call([Arg(0), Arg(0).shape[1], Arg(0).strides[1]])
def process_columns(values: Const(Float64[:, ::Strided])) -> None: ...

# C: void get_values(int n, double *out);
@native_call([Arg(0), Return(0)])
def get_values(n: Int) -> Float64[n]: ...

# C: int context_create(struct context **out);
@native_call(
    [Ptr(Return(0))],
    returns=Status[Int, Check(success=0, raises=RuntimeError)],
)
def context_create() -> Annotated[context, Owned, FreeWith("context_destroy")]: ...
```

Phase 2 also introduces policies and coercions such as:

- Python `str` to configured native text conversion;
- callback thunk creation and lifetime/exception handling;
- `Pack` and `CopyBack` for non-contiguous arrays;
- opaque handles and native ownership management;
- status conversion and hidden native outputs;
- derived NumPy metadata such as `Arg(i).shape`, `Arg(i).shape[...]`,
  `Arg(i).strides[...]`, `Arg(i).size` and `Arg(i).itemsize`.

None of these transformations is necessary to complete Phase 1.

### 15. Decisions Deferred Beyond Phase 1

The following decisions do not block the identity-call implementation:

1. Final implementation order within Phase 2 transformations.
2. Bare-string convenience defaults, writable text buffers and arrays of
   strings.
3. Callback policies beyond the basic future design direction.
4. Convenience construction of pointer rows from nested Python sequences and
   other high-level builders for `T **` and deeper graphs. Direct
   `Ptr[n](T)` pointer objects are already Phase 1 identity values.
5. Converting native pointer returns into NumPy views beyond explicitly shaped,
   explicitly owned or borrowed storage. Returning direct `Ptr(T)` objects is
   already identity behavior.
6. Automatic derivation of hidden layout/stride arguments and packing or
   copy-back for storage the native routine does not accept directly.
7. Clean generated `.pyi` files for IDEs and type checkers.
8. Module/library selection, platform variants and non-default calling
   conventions.
9. Unions, writable native globals and variadic functions.

No deferred behavior may be silently inferred by the Phase 1 wrapper
generator.
