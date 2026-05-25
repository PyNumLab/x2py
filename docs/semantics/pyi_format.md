# Wrapper `.pyi` Format

The semantic `.pyi` format is a Python-valid view of x2py semantic IR. It is
language-neutral: Fortran and future C inputs use the same type, storage,
pointer, array, layout and metadata notation. Source language differences are
represented by contracts and metadata, not by separate syntax families.

This document describes the behavior implemented for the current Fortran path
and the shared notation used by the first C semantic conversion subset. C
`.pyi` generation remains deferred.

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
def assumed(x: Annotated[Float64[::Strided, ::Strided], ORDER_F]) -> None: ...
```

There is no separate dimension helper in canonical type syntax. A dimension
entry without colons is an extent (`Float64[n]`, `Float64[n, m]`). Slice-like
entries express range or stride contracts (`Float64[1:n]`,
`Float64[::Strided]`, `Float64[:, 0:n:m]`). `Strided` means the runtime stride
is part of the accepted storage contract.

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

## Preserved Metadata

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

## Loading And Round Trips

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

## Pythonic Projection (Later)

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

### Native Argument Projection

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

### Coercions And Constraints

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

### Validation Contracts

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
exact-reference adaptation, coercion/contract execution or C `.pyi` output.

## Deferred C Work

The shared model represents the current C semantic conversion subset for
functions, variables,
fields, constants, scalar references, pointers, arrays with known contracts,
origin metadata, mutability and ownership facts. Remaining C work includes:

- C `.pyi` generation;
- C wrapper lowering;
- C ownership, callback or pointer policy inference.

Future C conversion should use the same notation: by-value scalars as bare
types, unrefined pointers as `Ptr(T)` or `Ptr(Const(T))`, and array notation
only when a real array storage contract is known.
