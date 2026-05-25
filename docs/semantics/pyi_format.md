# Wrapper `.pyi` Format

The `.pyi` format is a Python-valid view of the semantic IR. It is meant to be
easy to read and edit first, with extra metadata added only when the wrapper
needs information that normal Python annotations cannot express.

The target canonical editable form uses NumPy-style array subscriptions and
keeps non-dimensional semantic constraints in `Annotated[...]` metadata. For
example, an ordinary Fortran array accepted from Python is a NumPy array:

```python
def norm2(
    x: Const(Float64[:])
) -> Float64: ...
```

Unqualified array notation has one meaning independent of source language:
`Float64[:, :]` implies `ORDER_C`, matching ordinary NumPy notation and
allocation defaults. A generator translating an ordinary Fortran-contiguous
multidimensional array contract emits
`Annotated[Float64[:, :], ORDER_F]`; it does not rely on the fact that the
stub originated from Fortran. A contiguous rank-one array needs no order
metadata because C- and Fortran-contiguous vector storage is the same.
For rank two or higher, stride capability and order are separate constraints:
bare `Float64[::Strided, ::Strided]` is strided with implicit `ORDER_C`,
while `Annotated[Float64[::Strided, ::Strided], ORDER_F]` is a strided
Fortran-oriented contract. A fully orientation-independent contract is written
`Annotated[Float64[::Strided, ::Strided], ORDER_ANY]`.
On a strided form, `ORDER_F` is not a requirement that NumPy report the view
as `F_CONTIGUOUS`; it preserves the required native orientation while
non-unit strides remain allowed.

NumPy normally creates a new multidimensional array in C order. A caller of a
dense `Annotated[T[:, :], ORDER_F]` signature supplies F-contiguous storage,
for example using `np.empty(shape, order="F")` or
`np.asfortranarray(value)`, unless an explicit wrapper conversion policy is
later introduced. An `ORDER_F` form containing `::Strided` instead supplies
Fortran-oriented storage satisfying its stated stride constraints; it is not
required to be contiguous.

The current parser and printer still emit and consume the earlier
`Float64[Shape(':'), ORDER_F]` representation and existing Python-facing
output projections. They must migrate before this exact native target notation
is accepted as a runnable or round-trippable stub.

Emit currently supported stubs from semantic IR with `emit_module`:

```python
from semantics.pyi_printer import emit_module

pyi = emit_module(module)
```

## Default: Exact Native Interface

The default semantic `.pyi` represents the direct C callable interface and the
exact Fortran dummy-argument contract. It does not use `@native_call`:

- Every target argument remains a visible Python argument in target order.
- A direct native return is the only value placed in the return annotation.
- A scalar passed through writable native storage is written `Ptr(T)`.
- A scalar passed through read-only native storage is written `Ptr(Const(T))`.
- A Fortran array accepted from Python is represented by a NumPy array
  annotation, together with any source-level properties the wrapper must
  preserve, such as rank, shape, `ORDER_F`, `Allocatable` or
  `Pointer`.
- A C pointer uses an array annotation only when an array storage contract is
  known; an otherwise unrefined `T *` remains `Ptr(T)`.

For a primitive scalar argument, `Ptr(T)` means that Python supplies writable
zero-dimensional NumPy storage of the matching dtype. `Ptr(Const(T))` means
the corresponding read-only native reference contract. A plain Python scalar
does not satisfy either exact reference form because creating temporary storage
would already be a Pythonic adaptation.

### Fortran Direct Form

For Fortran, "exact" means that the semantic stub preserves the target
procedure's dummy-argument contract. The wrapper backend may emit an
intermediary Fortran procedure that accepts C/Python-provided storage and
calls the desired Fortran procedure. Creating the compiler-required
descriptor, temporary or association inside that intermediary is native
lowering; it is not an `@native_call` Pythonic projection, provided the
visible semantic arguments and results are unchanged.

Fortran scalar dummy arguments that are passed by reference remain reference
arguments in the exact interface. `intent(out)` and `intent(inout)` differ in
source-language intent, but both require writable caller-supplied storage and
do not become Python results in this form:

```fortran
subroutine update(scale, value, result) bind(c)
  use iso_c_binding
  real(c_double), value, intent(in) :: scale
  real(c_double), intent(inout) :: value
  real(c_double), intent(out) :: result
end subroutine
```

```python
def update(
    scale: Float64,
    value: Ptr(Float64),
    result: Ptr(Float64),
) -> None: ...
```

A read-only Fortran reference is represented without permitting mutation:

```fortran
subroutine inspect(value) bind(c)
  use iso_c_binding
  integer(c_int), intent(in) :: value
end subroutine
```

```python
def inspect(value: Ptr(Const(Int32))) -> None: ...
```

Fortran array lowering is determined by the dummy declaration, not simply by
whether the source is modern or legacy:

| Fortran dummy array form or property | Exact semantic annotation | Backend obligation |
| --- | --- | --- |
| explicit-shape or adjustable, such as `x(n, m)` | `Annotated[Float64[n, m], ORDER_F]` | Validate extents and pass first-element Fortran-contiguous storage. |
| assumed-size, such as `x(*)` or `x(n, *)` | `Float64[:]` for rank one; `Annotated[Float64[:, :], ORDER_F]` or the known-rank equivalent for multidimensional contiguous storage | Preserve known rank/bounds; no final extent is supplied by the dummy. |
| assumed-shape, such as `x(:)` or `x(:, :)`, without `contiguous` | `Float64[::Strided]` for a vector; `Annotated[Float64[::Strided, ::Strided], ORDER_ANY]` for an unrestricted rank-two contract | Construct the Fortran call representation from NumPy shape and strides. Use `ORDER_C` (implicit) or `ORDER_F` instead when the contract deliberately restricts orientation. |
| assumed-rank, `x(..)`, without `contiguous` | stride-aware rank-polymorphic notation with `ORDER_ANY` once defined | Pass runtime rank, shape and strides as required by the generated adapter. |
| `contiguous` dummy property | `Float64[:]` for rank one; `Annotated[Float64[:, :], ORDER_F]` or the corresponding form for rank two or higher | Reject or explicitly convert incompatible layout according to policy. |
| `allocatable` dummy property | `Annotated[Float64[:], Allocatable]` for a vector; add `ORDER_F` only for a multidimensional Fortran-contiguous contract | Provide allocatable semantics and preserve allocation changes if permitted. |
| `pointer` dummy property | `Annotated[Float64[:], Pointer]` for a contiguous vector, or a stride-aware form when permitted; combine with `ORDER_F` or `ORDER_ANY` for multidimensional storage as required | Provide pointer association semantics and preserve association changes if permitted. |

No additional annotation is needed for the compiler's internal array
transport. The target is already known to be Fortran, and the backend's
intermediary Fortran procedure can prepare the compiler-specific argument
representation. The `.pyi` must say whether the target contract is
sufficiently known: element type, rank or allowed ranks, required
extents/bounds, mutability, contiguity requirements and attributes such as
`Allocatable` or `Pointer`.

This design assumes that the intermediary is compiled against an available
Fortran interface, for example by `use`-associating a module procedure or by
using retained source/semantic information sufficient to declare that
interface. If a wrapper must call an arbitrary precompiled non-interoperable
Fortran symbol using only a `.pyi` file and a binary library, compiler ABI and
dummy-category information must be retained separately; NumPy shape
annotations alone cannot discover that call convention.

`Float64[...]` is not a placeholder for missing information: it represents a
target procedure that accepts runtime rank, such as an assumed-rank dummy. If
a fixed-rank target's required rank, dimensions or attributes are unknown,
the interface is incomplete and should fail readiness rather than silently
be generalized.

Plain dense array notation means C-contiguous storage. Multidimensional
Fortran-contiguous contracts are emitted with explicit `ORDER_F`; rank-one
contiguous arrays need no order marker. For multidimensional strided storage,
the order annotation is retained independently: a bare strided form is
C-oriented, an `ORDER_F` strided form is Fortran-oriented, and `ORDER_ANY`
states that neither orientation is required. An ordinary assumed-shape dummy
without `contiguous` can accept a non-contiguous actual argument in any
orientation when the adapter passes its shape and strides correctly. These
are distinct contracts:

```python
# Explicit-shape Fortran-contiguous storage.
def explicit_shape(
    n: Ptr(Const(Int32)),
    m: Ptr(Const(Int32)),
    x: Annotated[Float64[n, m], ORDER_F],
) -> None: ...

# Assumed-shape with a stated contiguous Fortran storage requirement.
def assumed_shape(
    x: Annotated[Float64[:, :], ORDER_F],
) -> None: ...

# Strided storage with the default C orientation.
def c_oriented_strided(
    x: Float64[::Strided, ::Strided],
) -> None: ...

# Strided storage with a required Fortran orientation.
def f_oriented_strided(
    x: Annotated[Float64[::Strided, ::Strided], ORDER_F],
) -> None: ...

# Assumed-shape exposing the unrestricted non-contiguous contract.
def any_order_assumed_shape(
    x: Annotated[Float64[::Strided, ::Strided], ORDER_ANY],
) -> None: ...
```

At the Python boundary, each of these array arguments is still a NumPy array.
For an ordinary assumed-shape or assumed-rank dummy, NumPy already provides
the storage facts an adapter needs: data address, element dtype/length, rank,
extents and strides. The properties that change semantics beyond those array
facts must remain in the annotation:

| Fortran property | Representation | Observable consequence |
| --- | --- | --- |
| Required dense Fortran-contiguous multidimensional storage | `Annotated[T[:, :], ORDER_F]` or shaped equivalent | May reject a C-order or strided input or require an explicit conversion policy. |
| C-oriented multidimensional strided storage | `T[::Strided, ::Strided]` | Strides are admitted while the default order remains `ORDER_C`. |
| Fortran-oriented multidimensional strided storage | `Annotated[T[::Strided, ::Strided], ORDER_F]` | Strides are admitted while retaining Fortran orientation. |
| Orientation-independent multidimensional strided storage | `Annotated[T[::Strided, ::Strided], ORDER_ANY]` | Suitable for an unrestricted assumed-shape dummy. |
| Rank-one contiguous storage | `T[:]` or `T[n]` without an order marker | C- and Fortran-contiguous storage are equivalent for a vector. |
| Rank-one non-contiguous storage | `T[::Strided]` or a bounded/exact-step equivalent | Stride, not C/F order, distinguishes the view. |
| Allocation semantics | `Allocatable` | A target may allocate, deallocate or reallocate; replacing storage cannot be observed merely by mutating the original NumPy array. |
| Pointer association semantics | `Pointer` | A target may change association; reassociation cannot be expressed by element updates on the original NumPy array. |
| Required explicit bounds not recoverable from NumPy shape | retained bound metadata | The adapter constructs matching Fortran bounds rather than assuming Python's zero-based view is the complete contract. |

For ordinary Fortran-contiguous array dummies, element mutation is observed
through the supplied NumPy storage:

```python
def axpy(
    n: Ptr(Const(Int32)),
    a: Ptr(Const(Float64)),
    x: Const(Float64[n]),
    y: Float64[n],
) -> None: ...
```

A legacy Fortran 77 style explicit-shape or assumed-size array is lowered
through its first element address, not through a descriptor. Its dimensions
still belong in the semantic annotation when they are known, because the
wrapper can validate NumPy storage before passing that address:

```fortran
      SUBROUTINE SCALE(N, X)
      INTEGER N
      DOUBLE PRECISION X(N)
```

```python
def scale(
    n: Ptr(Const(Int32)),
    x: Float64[n],
) -> None: ...
```

The same first-element-address rule also applies to modern explicit-shape and
assumed-size dummy arrays. By contrast, modern assumed-shape, assumed-rank,
`Pointer` and `Allocatable` dummies require their richer Fortran call
representation internally; the generated intermediary handles that transport.
For a first-element-address interface, a non-contiguous NumPy view cannot be
passed directly because the target procedure receives no stride information.
For rank greater than one, explicit `ORDER_F` also makes NumPy element order
match Fortran column-major indexing. Accepting other layouts for these
interfaces requires an explicit pack/copy-back policy.

For an allocatable or pointer dummy, using a NumPy argument is still the
desired Python-facing API, but state-changing operations need an explicit
policy. Reading data or changing elements can be adapted directly. Allocating
a replacement, deallocating storage or changing pointer association must later
define whether the wrapper rejects the operation, copies data back, or
returns/manages new storage:

```python
def maybe_resize(
    x: Annotated[Float64[:], Allocatable],
) -> None: ...

def maybe_reassociate(
    x: Annotated[Float64[:], Pointer],
) -> None: ...

# Pointer dummy permitted to associate with a non-contiguous section.
def pointer_section(
    x: Annotated[Float64[::Strided], Pointer],
) -> None: ...

def pointer_matrix_section(
    x: Annotated[Float64[::Strided, ::Strided], ORDER_F, Pointer],
) -> None: ...
```

Until that policy exists, mutable `Allocatable` or `Pointer` dummies whose
allocation or association can change are wrap-readiness blockers; they must
not be silently treated as ordinary borrowed arrays.

`Pointer` may be combined with `::Strided` when the target permits
association with a non-contiguous section. `Allocatable` is not the general
strided-view spelling: allocated array storage is contiguous, while its
distinct issue is allocation ownership and possible replacement.

### C Direct Form

C by-value parameters and direct returns use bare types. C scalar pointers use
the same reference notation as Fortran:

```c
int add(int a, int b);
void increment(int *value);
void read_count(const int *value);
```

```python
def add(a: Int, b: Int) -> Int: ...
def increment(value: Ptr(Int)) -> None: ...
def read_count(value: Ptr(Const(Int))) -> None: ...
```

For `increment`, a caller supplies scalar storage rather than a Python `int`:

```python
value = np.array(7, dtype=np.intc)
increment(value)
updated = value.item()
```

C has no generated Fortran adapter for an ordinary pointer parameter. A bare
C pointer with no known scalar or array storage contract is kept as a raw
pointer:

```c
void consume(double *values);
double sum_values(size_t n, const double *values);
```

```python
def consume(values: Ptr(Float64)) -> None: ...
def sum_values(n: SizeT, values: Const(Float64[n])) -> Float64: ...
```

`Float64[n]` in the second signature records an API/semantic shape contract
and still lowers to one `double *`; it does not claim C passes rank or shape
metadata inside `values`.

### Direct Returns

Native returns remain returns:

```python
def value() -> Float64: ...
def raw_values() -> Ptr(Float64): ...
```

An output parameter is not a native return. For example, a Fortran subroutine
`make_vector(n, x)` with an output array and a C function
`void get_count(int *out)` remain:

```python
def make_vector(
    n: Ptr(Const(Int32)),
    x: Float64[n],
) -> None: ...
def get_count(out: Ptr(Int)) -> None: ...
```

## Pythonic Projection (Later)

A later optional generation mode, for example `--pythonic`, may expose a
friendlier Python interface that differs from the native argument list. Only
that projected view uses `@native_call`.

For a mutable scalar reference, the exact form is:

```python
def increment(value: Ptr(Int)) -> None: ...
```

A generated Pythonic form may accept and return an ordinary scalar while the
decorator records the native reference and readback:

```python
@native_call([Ptr(Arg(0))])
def increment(value: Int) -> Returns["value", Int]: ...
```

The same transformation applies to a Fortran scalar `intent(inout)` argument:

```python
# Exact Fortran interface
def advance(value: Ptr(Float64)) -> None: ...

# Optional Pythonic generated view
@native_call([Ptr(Arg(0))])
def advance(value: Float64) -> Returns["value", Float64]: ...
```

For a native output argument, a Pythonic view may allocate and return storage:

```python
# Exact native interface
def get_count(out: Ptr(Int)) -> None: ...

# Optional Pythonic generated view
@native_call([Ptr(Return(0))])
def get_count() -> Int: ...
```

Pythonic generation can also derive array metadata using NumPy attributes:

```python
# Exact native interface: C size argument remains visible.
def sum_values(n: SizeT, values: Const(Float64[n])) -> Float64: ...

# Optional Pythonic generated view.
@native_call([As[SizeT](Arg(0).shape[0]), Arg(0)])
def sum_values(values: Const(Float64[:])) -> Float64: ...
```

`Arg(i).shape[dim]` selects a zero-based axis extent.
`Arg(i).strides[dim]` selects NumPy's byte stride for one axis:

```python
@native_call([Arg(0), Arg(0).shape[1], Arg(0).strides[1]])
def process_columns(values: Const(Float64[:, ::Strided])) -> None: ...
```

Annotation steps such as `::m` are element steps, while
`Arg(i).strides[dim]` is measured in bytes. A native function expecting an
element stride requires an explicit conversion using `Arg(i).itemsize`.

This projected syntax is a design target, not behavior currently implemented
by the parser or printer.

## Type Constraints

Array dimensions use NumPy-style subscriptions. `Annotated[...]` holds layout
or Fortran dummy-argument properties that do not describe dimensions:

```python
# Plain array notation is always C-order; generated C stubs use it directly.
Float64[:, :]

# Generated dense Fortran-contiguous contracts explicitly state ORDER_F.
Annotated[Float64[:, :], ORDER_F]

# Rank-one order is not emitted: ORDER_C and ORDER_F are equivalent.
Annotated[Int32[n], Allocatable]
Annotated[Float64[:], Pointer]

# For rank >= 2, stride capability and orientation are independent.
# Bare strided storage keeps the default ORDER_C interpretation.
Float64[::Strided, ::Strided]
Annotated[Float64[::Strided, ::Strided], ORDER_F]
Annotated[Float64[::Strided, ::Strided], ORDER_ANY]

# For rank one, stride is relevant but C/F order is not.
Float64[::Strided]
```

Dimension forms include:

- `T[:]` for a rank-one array of unspecified extent.
- `T[:, :]` for a rank-two array of unspecified extents.
- `T[n]` for a rank-one array whose size is `n`; this is an extent, not an
  element selection or index.
- `T[n, m]` or `T[3, 4]` for a rank-two array whose axis sizes are given by
  the respective symbolic or literal extents.
- `T[0:n]` or `T[start:stop]` for an explicit half-open range contract rather
  than a size-only contract.
- `T[:, ::Strided]` for a rank-two array whose second axis carries a runtime
  stride rather than an assumed contiguous step.
- `T[::Strided, ::Strided]` for a rank-two array that exposes arbitrary
  runtime strides on both axes while retaining the default `ORDER_C`
  orientation.
- `T[:, ::2]` for a rank-two array whose second-axis step is exactly two.
- `T[:, 0:n:Strided]` for a bounded second axis with an arbitrary runtime
  stride.
- `T[:, 0:n:m]` for a bounded second axis whose step is the semantic value
  `m`.

`T[:, ::]` is valid Python syntax, but it has the same meaning as `T[:, :]`;
it does not declare stride-aware storage. Use `::Strided` when an axis stride
must be represented and validated.

An axis entry without colons is an extent: `T[n]` has size `n`, and
`T[n, m]` has shape `(n, m)`. An axis slice follows the NumPy/Python-style
half-open `lower:upper:step` shape. Each bound or explicit step may be a
literal or a symbol resolved from a visible scalar argument or a declared
semantic constant such as `Final[Int32]`. For example, in
`def sample(n: Int32, m: Int32, x: T[:, 0:n:m]) -> None: ...`, `n`
constrains the selected upper bound and `m` constrains the exact step.
`Strided` is the sentinel for any runtime step when its exact value is not
part of the semantic contract. Future expression support can extend symbols
to resolvable arithmetic such as `2*n` without changing this notation. Steps
are measured in elements, following NumPy slicing; conversion to native byte
strides, when required, belongs to the native-call mapping.

For a Fortran assumed-shape or assumed-rank target lowered through a generated
Fortran intermediary, `Strided` can be satisfied directly from NumPy stride
metadata: it does not introduce another public function argument. For a C
function, or for a Fortran first-element-address interface, stride-aware
storage is direct only when the target call has the necessary visible stride
metadata; otherwise it requires packing/copy-back.

Rank-polymorphic arrays use `...`, optionally followed by an allowed-rank
selector:

| Annotation | Meaning |
| --- | --- |
| `Float64[...]` | `Float64` array with any rank (any number of dimensions). |
| `Float64[...][1:4]` | `Float64` array with rank 1, 2, or 3; the stop value is exclusive. |
| `Float64[...][1, 2, 5]` | `Float64` array with rank 1, 2, or 5. |

Layout and ownership constraints can follow a dimension form:

- Unqualified array forms imply `ORDER_C`, including multidimensional forms
  with `::Strided`, regardless of whether a stub was generated from C,
  Fortran, or written by hand. Generated C stubs omit redundant `ORDER_C`;
  for rank one this same bare form is also the canonical Fortran spelling
  because C/F order is not distinct.
- A Fortran generator emits `Annotated[Float64[:, :], ORDER_F]` for a
  Fortran-contiguous rank-two or higher array contract rather than relying on
  language provenance.
- `Annotated[Float64[...][1:4], ORDER_F]` writes a Fortran-oriented
  contract for ranks 1, 2 or 3; concrete dense axis forms state
  contiguity where required.
- `Annotated[Float64[::Strided, ::Strided], ORDER_F]` combines permitted
  runtime strides with a required Fortran orientation.
- `Annotated[Float64[::Strided, ::Strided], ORDER_ANY]` combines permitted
  runtime strides with no C/F orientation restriction, for example for a
  fully general Fortran assumed-shape dummy.
- `ORDER_F` for a required Fortran orientation; with dense axis forms it
  expresses Fortran-contiguous storage, while with `::Strided` it does not
  prohibit non-contiguous storage.
- `ORDER_ANY` for a multidimensional contract that imposes no C/F
  orientation requirement.
- `ORDER_C` is redundant in the canonical format: use the bare array form
  because it already means the C orientation; a bare dense form is
  C-contiguous, while a bare strided form is C-oriented and non-contiguous
  where its stride constraints permit it.
- `Allocatable` for a Fortran allocatable dummy or value.
- `Pointer` for a Fortran pointer dummy; this is not the same as `Ptr(T)`,
  which expresses a scalar or unrefined native address parameter.
- `Const(...)` for read-only pointee or array-storage contracts.
- `Ptr(T)` and `Ptr(Const(T))` for one-level scalar/native reference
  arguments, rather than array dimensions.

For a Fortran target, array notation describes the NumPy value accepted at
the Python boundary and the Fortran array contract the adapter must satisfy.
It does not expose whether the compiler-level call uses an address or a
descriptor. For a C target, dimensioned array notation records a known
storage contract and lowers to one native data pointer. Bare array forms
always imply `ORDER_C`. For rank one, a contiguous Fortran array uses the
same bare form because `ORDER_C == ORDER_F` for vectors. For rank two or
higher, Fortran-oriented contracts retain `ORDER_F` explicitly in generated
Fortran stubs, whether dense or strided. When a Fortran assumed-shape/rank
procedure accepts non-contiguous storage in any multidimensional orientation,
use a form such as
`Annotated[T[::Strided, ::Strided], ORDER_ANY]`; use `T[::Strided]` for a
rank-one form because rank-one C/F order is not distinct.
A Fortran adapter intentionally designed around C-contiguous multidimensional
storage may use the plain array form because that contract is genuinely
`ORDER_C`.

`Strided` is an axis constraint, while `ORDER_C`, `ORDER_F`, and `ORDER_ANY`
describe multidimensional orientation independently. Consequently,
`T[::Strided, ::Strided]` inherits `ORDER_C`,
`Annotated[T[::Strided, ::Strided], ORDER_F]` admits strides under a Fortran
orientation, and `Annotated[T[::Strided, ::Strided], ORDER_ANY]` makes no
orientation restriction. An implementation must not reduce `ORDER_F` on a
strided form to the NumPy `F_CONTIGUOUS` flag. Wrappers must either pass the
required native stride metadata or apply an explicit packing/copy-back policy.
A Fortran adapter can prepare the target array argument from NumPy shape and
strides; a direct C call needs any required native extent or stride scalar
arguments preserved in the exact signature.

The alternative spelling `T[:, :][ORDER_F]` is deliberately not canonical:
it can be confused with the second subscription used for permitted-rank
selectors such as `T[...][1:4]`. Use
`Annotated[T[:, :], ORDER_F]` for layout properties.

`Arg(i).shape[dim]` and `Arg(i).strides[dim]` are native-call projection
expressions for obtaining metadata from a visible array argument; they are not
array annotation syntax.

## Constants

Fortran `parameter` declarations are constants. The printer emits them with
`Final[...]` instead of a generic type constraint:

```python
answer: Final[Int32]
scale: Final[Float64]
```

When a constant is private, `private[...]` remains the outer visibility marker:

```python
hidden_answer: private[Final[Int32]]
```

The `.pyi` parser accepts `Final[...]` and restores it to the semantic IR as a
`Constant` constraint, so edited stubs still round-trip through the existing IR
model.

## Visibility

Private procedures and classes use decorators:

```python
@private
def hidden(x: Int32) -> None: ...
```

Private module variables and fields use `private[...]`:

```python
hidden_scale: private[Float64]
```

## Imports

Plain module imports are emitted for bare Fortran `use` statements:

```python
import iso_c_binding
```

For explicit `use ... only:` lists, the printer emits Python `from` imports so
the imported symbols remain visible in the stub:

```python
from iso_c_binding import c_int, c_double
```

For renamed Fortran imports, both sides are preserved with Python alias syntax:

```fortran
use list_input, delete_input => delete_input_list
```

```python
from list_input import delete_input_list as delete_input
```

The `.pyi` parser accepts both `import module` and
`from module import source as target`. In semantic IR, `source` is the
provider-side name and `target` is the local alias; when there is no alias,
`target` is `None`.

## Fortran Names That Are Not Python Identifiers

If a parameter name is not usable as Python syntax, the printer uses a safe
Python name and preserves the original name with `Annotated[..., Name(...)]`:

```python
def call(
    class_: Annotated[Int32, Name("class")]
) -> None: ...
```

Module variables and derived-type fields can use `var[...]`:

```python
var["operator-name"]: Float64
```

Both forms are valid Python syntax and are understood by the `.pyi` parser.

## Loading Edited Stubs

Use these entrypoints to recover semantic IR from a stub:

```python
from semantics.pyi_parser import convert_pyi_to_ir, load_pyi_file, parse_pyi_text

module = load_pyi_file("mymodule.pyi")
module = parse_pyi_text(source, module_name="mymodule")
module = convert_pyi_to_ir(source, module_name="mymodule")
```

To compare an edited `.pyi` file with an existing semantic IR module:

```python
from semantics.pyi_parser import load_pyi_file

edited_ir = load_pyi_file("mymodule.pyi", module_name=existing_ir.name)
assert edited_ir == existing_ir
```

An exact semantic stub preserves every visible target argument required to
issue the call. For C this is the direct native argument list; for Fortran it
is the target dummy-argument contract lowered through the generated adapter.
A plain return type means a direct target return. `Returns[...]` and
`@native_call` belong to a later Pythonic projected stub, where a generated
wrapper intentionally turns caller-supplied storage into Python return values.

Function and method argument names are placeholders during IR comparison. For
example, `def f(a: Int32) -> None: ...` and
`def f(b: Int32) -> None: ...` compare equal as functions. The same positional
renaming is applied inside dimension expressions such as `Float64[n]`. Names
outside function and method argument lists, including module variables and class
fields, remain significant.

## Semantic Wrap-Readiness

Readiness is assessed from semantic IR, not from parser internals. The same CLI
flag works for either source path:

```bash
python -m x2py solver.f90 --wrap-readiness
python -m x2py solver.pyi --wrap-readiness
```

For Fortran input, x2py parses the source, converts it to semantic IR, then
checks that semantic interface. For `.pyi` input, x2py parses the edited stub
directly to semantic IR and checks that interface. The edited `.pyi` is the
source of truth when the user needs to provide information the source parser
cannot infer.

The flag can be requested alone for a concise readiness report or combined with
other stages. For example, `--semantics --wrap-readiness` emits semantic IR with
the readiness payload attached.

The target readiness check consumes these `.pyi` facts:

- `class name:` declares a wrapper-visible derived type or handle.
- `name: Final[Int32] = 8` declares a literal compile-time constant value that
  can satisfy shape and size metadata.
- `Callable[[ArgType, ...], ReturnType]` declares the full callback signature
  for a procedure/function-pointer argument.
- Array annotations and `Annotated[...]` properties provide required rank,
  shape, layout, `Allocatable` and `Pointer` facts for a Fortran adapter.

Mutable `Allocatable` or `Pointer` array dummies that may replace allocation
or pointer association remain not ready until a return, ownership or
copy-back policy specifies how that changed state is exposed to Python.

Example:

```python
from typing import Callable, Final

rk: Final[Int32] = 8

class sim_state:
    n: Int32
    values: Float64[n]

def step(
    state: Ptr(sim_state),
    t: Ptr(Const(Float64)),
    objective: Callable[[Ptr(sim_state), Ptr(Const(Float64))], Float64],
    score: Ptr(Float64),
) -> None: ...
```

This can clear readiness blockers for a Fortran routine that imports
`sim_state`, uses `real(kind=rk)`, accepts `objective` as a callback, and
mutates caller-supplied `state`/`score` storage. A `Final[...]` declaration
without a literal value is intentionally not enough for compile-time shape or
size resolution, and `Callable[..., ReturnType]` is not enough for callbacks
because the wrapper still needs argument order and argument types.
