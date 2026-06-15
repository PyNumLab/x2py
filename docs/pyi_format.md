# Semantic `.pyi` Format

Semantic `.pyi` files are x2py's editable wrapper contract. They are valid
Python stub files, but they are not meant to be clean static-type-checker stubs.
They preserve native type, storage, ownership, shape and visibility facts that a
future wrapper generator needs.

Status terms used below:

- **Generated**: emitted today by `--pyi` or `codegen.printers.pyi_printer`.
- **Loaded**: accepted today by `semantics.pyi_parser` and converted back to
  semantic IR.
- **Readiness**: understood by the semantic readiness checker.
- **Roadmap**: design direction, not implemented wrapper behavior.

The scalar dtype mapping behind these names is documented in
[semantics.md](semantics.md). Wrapper-policy gaps are tracked in
[wrapper_design_notes.md](wrapper_design_notes.md).

## File Shape

Loaded files support imports, classes, enums, variables and stub functions:

```python
from types_mod import particle

answer: Final[Int32]

class particle:
    id: Int32
    mass: Float64

def scale(
    n: Ptr(Const(Int32)),
    values: Float64[n],
) -> None: ...
```

Function and method bodies must be `...`. Positional-only, keyword-only,
`*args`, `**kwargs`, untyped parameters and ordinary Python statements are not
part of the semantic format.

`load_pyi_modules(...)` can load one file, several files, or a directory tree.
Directory loading derives dotted module names from relative `.pyi` paths and
reconciles imported external type references across the loaded set.

## Semantic Type Names

The public annotations use semantic names, not raw C or Fortran spellings:

| Family | Names |
| --- | --- |
| Booleans and generic values | `Bool`, `Any` |
| Signed integers | `Int`, `Int8`, `Int16`, `Int32`, `Int64` |
| Unsigned integers | `UInt8`, `UInt16`, `UInt32`, `UInt64`, `SizeT` |
| Reals | `Float32`, `Float64`, `Float128` |
| Complex | `Complex64`, `Complex128`, `Complex256` |
| Text | `String` |
| User types | class names, enum names and imported type names |
| Callables | `Callable`, `Callable[..., T]`, `Callable[[A, B], T]` |

`Unknown` is intentionally rejected in `.pyi` annotations. Generated stubs must
resolve or block unsupported source types instead of emitting unknown contracts.
Current C callback placeholders such as `CFunctionPointer` can appear in
generated stubs when source callback policy is incomplete; edit them to a full
`Callable[[...], ...]` contract before expecting readiness to pass.

## Storage Contracts

Bare types are direct values:

```python
def dot(a: Float64, b: Float64) -> Float64: ...
```

`Ptr(T)` represents native pointer-backed or reference storage:

```python
def update(value: Ptr(Float64)) -> None: ...
def inspect(value: Ptr(Const(Int32))) -> None: ...
```

`Const(T)` marks the wrapped storage read-only. For a pointer this means a
read-only pointee. For an array it means read-only array storage.

Pointer depth is explicit for low-level pointer graphs:

```python
handle: Ptr[2](OpaqueHandle)
argv: Ptr[3](Const(Int8))
```

`Ptr[1](T)` is invalid; use `Ptr(T)`.

Array storage uses NumPy-style subscriptions:

```python
vector: Float64[:]
fixed: Float64[3]
matrix: Float64[n, m]
strided: Float64[::Strided]
rank_polymorphic: Float64[...]
```

Dimension entries have the following meaning:

| Form | Meaning |
| --- | --- |
| `:` | unconstrained extent for that axis |
| `n`, `3`, `n + 1` | required extent expression |
| `lower:upper` | range-like storage expression |
| `::Strided` | axis accepts runtime stride |
| `0:n:Strided` | range plus stride-aware axis |
| `...` | rank-polymorphic storage |

Qualified names such as `foo.bar` are not accepted as dimension expressions.
Use local constants or generated `Final[...]` names for shape symbols.

## Metadata With `Annotated`

`Annotated[...]` carries storage metadata and semantic constraints:

```python
def fill(
    a: Annotated[Float64[:, :], ORDER_F],
    out: Annotated[Ptr(Float64), Intent("out")],
) -> None: ...
```

Generated canonical metadata:

| Metadata | Meaning |
| --- | --- |
| `ORDER_F` | multidimensional Fortran-oriented storage |
| `ORDER_ANY` | edited contract accepts either C or Fortran orientation |
| `Allocatable` | Fortran allocatable array storage |
| `Pointer` | Fortran pointer array storage |
| `Intent("out")` | exact native argument is an output argument |
| `Name("native-name")` | source name cannot be represented directly as the Python target name |
| `FortranCharacterLength("n")` | Fortran character storage length for `String` contracts |
| `FortranAllocatable` | Fortran scalar character storage is allocatable |

Loaded compatibility metadata:

| Metadata | Meaning |
| --- | --- |
| `ORDER_C` | explicit C-oriented storage; this is also the default for plain multidimensional arrays |
| `Contiguous` | source provenance says the array is contiguous |
| `ArrayCategory("...")` | source array category provenance |
| `SourceDims(...)` | source declaration dimensions |
| `LowerBounds(...)`, `UpperBounds(...)` | source bound provenance |

Other positional `Annotated` helpers are preserved as semantic constraints:

```python
value: Annotated[Int32, Bounded(1, 8), Finite]
```

`Final[T]` is the only public constant spelling. Do not use
`Annotated[T, Constant]` or `T[Constant]`.

## Constants And Enums

Constants use `Final[T]`. Literal values are optional unless the value is needed
as a compile-time expression or enum initializer:

```python
nmax: Final[Int32]
answer: Final[Int32] = 42
```

C enums are open semantic enums. The enum class records the underlying storage
type, and enumerators remain module-level constants:

```python
class status(Enum[Int]):
    pass

STATUS_OK: Final[status] = 0
STATUS_RETRY: Final[status] = STATUS_OK + 1
```

Open means the listed names are known constants, not the only possible native
values.

## Classes And Native Type Markers

Fortran derived types and ordinary semantic classes use normal class syntax:

```python
class particle:
    id: Int32
    position: Float64[3]
```

C aggregate identity is explicit through base markers:

```python
class packet(CStruct):
    tag: UInt32

class scalar(CUnion):
    i: Int32
    x: Float64

class context(CStruct, Opaque):
    pass
```

| Marker | Meaning |
| --- | --- |
| `CStruct` | native C `struct` |
| `CUnion` | native C `union` |
| `CAnonymous` | generated nested anonymous C aggregate type |
| `Opaque` | type identity is known, but fields/layout are intentionally hidden |

Anonymous C aggregate members are represented as nested classes plus a generated
field that marks the anonymous member:

```python
class flags(CStruct):
    class anonymous_union_0_type(CUnion, CAnonymous):
        integer: Int
        real: Float32

    _anonymous_union_0: Annotated[anonymous_union_0_type, CAnonymousMember]
    tag: Int
```

The generated field preserves that the anonymous union is a real C member even
though C exposes its fields through the containing aggregate.

External opaque types can live in separate owner stubs:

```python
# types_mod.pyi
class particle(Opaque):
    pass

# physics.pyi
from types_mod import particle

def move(p: Ptr(particle)) -> None: ...
```

If the owner stub is later edited to include fields, the import is reconciled as
a wrapped external type without changing the importing file.

## Functions, Methods And Returns

Generated C and Fortran stubs currently describe exact native interfaces: they
do not hide length arguments, reorder parameters, synthesize output returns, or
guess pointer ownership.

Fortran scalar dummy arguments are generated as:

| Source argument | Generated semantic form |
| --- | --- |
| no `value`, `intent(in)` | `Ptr(Const(T))` |
| no `value`, `intent(out)` | `Annotated[Ptr(T), Intent("out")]` |
| no `value`, `intent(inout)` | `Ptr(T)` |
| `value` | direct `T` |
| function result | direct return annotation |

Loaded return forms:

```python
def f() -> None: ...
def g(x: Float64) -> Float64: ...
def split(x: Float64) -> tuple[Float64, Int32]: ...
def projected(x: Float64) -> Returns["x", Float64]: ...
```

`Returns["name", T]` records an output value associated with an argument name.
`Returns["name", T, Optional]` marks the returned output optional. Plain tuple
return components after the first are converted to generated output arguments.

Class methods use the same stub form. An untyped leading `self` is allowed in a
method and is not treated as a native argument.

## Generic Procedure Overloads

The x2py semantic `.pyi` format uses `@overload("specific_name")` to link one
Python-visible declaration to an ordinary concrete procedure declaration. This
decorator is x2py metadata; it is not `typing.overload` and must not be imported
from `typing`.

```python
@private
def convert_integer(value: Ptr(Const(Int32))) -> Int32: ...

@private
def convert_real(value: Ptr(Const(Float64))) -> Float64: ...

@overload("convert_integer")
def convert(value: Ptr(Const(Int32))) -> Int32: ...

@overload("convert_real")
def convert(value: Ptr(Const(Float64))) -> Float64: ...

class accumulator:
    @overload("accumulator_add_integer")
    def add(self, value: Ptr(Const(Int32))) -> None: ...

    @overload("accumulator_add_real")
    def add(self, value: Ptr(Const(Float64))) -> None: ...
```

Concrete specifics remain ordinary functions with their native names and
source visibility. Public specifics remain public; private specifics use
`@private`. `@native_call` is not emitted merely to restate an unchanged native
function name.

The loader resolves only the decorator string. It never guesses a target by
signature. The target must exist exactly once, each target may occur only once
in one overload set, and the public declaration must agree with the concrete
call signature and return type. Missing, duplicate, ambiguous, and incompatible
links are deterministic errors.

Python method names recover the native generic for ordinary operators. When
two distinct Fortran generics share one Python method, the decorator carries
the otherwise unrecoverable spelling:

```python
@overload("equivalent_values", generic="operator(.eqv.)")
def __eq__(self, other: value) -> Bool: ...
```

The optional `generic=` argument is restricted to a compatible operator or
assignment generic. It is currently emitted for `.eqv.` and `.neqv.`, which
would otherwise be indistinguishable from `operator(==)` and `operator(/=)`.

The generated C extension exposes one callable for each generic name. It
dispatches before conversion using the wrapped scalar dtype, array element
dtype and rank, or wrapped derived-type class. It does not use implicit numeric
coercion to choose an overload. Array shape, bounds, and layout are validated
by the selected concrete wrapper, but they do not distinguish overloads;
overloads that differ only in those properties are rejected during generation.

All specifics must have one compatible Python call shape. Parameter names and
keyword parsing use the first specific procedure's signature. A call that
matches no specific raises `TypeError`; duplicate dtype/rank signatures are a
deterministic generation error.

Wrapped derived types dispatch by their generated extension class. Fortran
`extends` relationships are preserved semantically but do not currently create
Python C-type inheritance, so a base-type overload is not a fallback for a
derived wrapper. Each accepted wrapped derived type needs an explicit specific
procedure. User-defined Python subclasses are not part of this runtime
contract.

## Defined Operators And Assignment

Defined operators use the same explicit link. The concrete function keeps its
full Fortran operand list, while the class declaration describes the Python
method call:

```python
@private
def add_vector_real(left: Ptr(Const(vector)), right: Ptr(Const(Float64))) -> vector: ...

@private
def add_real_vector(left: Ptr(Const(Float64)), right: Ptr(Const(vector))) -> vector: ...

class vector:
    @overload("add_vector_real")
    def __add__(self, right: Ptr(Const(Float64))) -> vector: ...

    @overload("add_real_vector")
    def __radd__(self, left: Ptr(Const(Float64))) -> vector: ...
```

Operand positions are fixed:

| Python method | Native operands |
| --- | --- |
| non-reflected binary method | `self` is operand 1; `other` is operand 2 |
| reflected binary method | `other` is operand 1; `self` is operand 2 |
| unary method | `self` is the only operand |
| comparison method | `self` is the Python left operand; reflected comparison metadata restores native order |

Return annotations must equal the concrete procedure result. The generated C
extension dispatches the Python slot before conversion by dtype, rank, and
wrapped extension class. Operator slots also accept a native Python scalar when
there is exactly one candidate precision in that integer, real, or complex
family; this is needed when CPython or NumPy invokes a reflected slot with a
built-in scalar. No match raises `TypeError`, and indistinguishable candidates
fail during generation. Three-argument `pow(value, exponent, modulus)` is not a
Fortran operator form and raises `TypeError`.

Mappings:

| Fortran generic | Python methods |
| --- | --- |
| binary `operator(+)` | `__add__`, `__radd__` |
| unary `operator(+)` | `__pos__` |
| binary `operator(-)` | `__sub__`, `__rsub__` |
| unary `operator(-)` | `__neg__` |
| `operator(*)`, `operator(/)`, `operator(**)` | `__mul__`/`__rmul__`, `__truediv__`/`__rtruediv__`, `__pow__`/`__rpow__` |
| `operator(==)`, `operator(/=)` | `__eq__`, `__ne__` |
| `operator(<)`, `operator(<=)`, `operator(>)`, `operator(>=)` | `__lt__`, `__le__`, `__gt__`, `__ge__` with reflected comparison routing |
| `operator(.and.)`, `operator(.or.)`, `operator(.not.)` | `__and__`/`__rand__`, `__or__`/`__ror__`, `__invert__` |
| `operator(.eqv.)`, `operator(.neqv.)` | `__eq__`, `__ne__` |

x2py does not infer in-place methods such as `__iadd__`. Python's fallback
therefore applies: an expression such as `value += other` may replace the
Python reference with the ordinary operator result rather than invoking
Fortran defined assignment.

A named operator `.custom.` is exposed as `operator_custom(self, other)`. If
the wrapped class is native operand 2, the method is
`r_operator_custom(self, other)`. These are normal methods because Python has
no syntax or data-model slot for arbitrary Fortran operator names.

Python assignment cannot be intercepted. Fortran `assignment(=)` is exposed as
explicit mutation:

```python
@private
def assign_vector_real(
    left: Annotated[Ptr(vector), Intent("out")],
    right: Ptr(Const(Float64)),
) -> None: ...

class vector:
    @overload("assign_vector_real")
    def assign(self, right: Ptr(Const(Float64))) -> None: ...
```

`lhs.assign(rhs)` invokes native `lhs = rhs`, mutates the existing wrapped
object, preserves Python object identity, and returns `None`. It never replaces
the Python variable. Assigning an object to itself is a no-op. A supported
specific must be a two-argument subroutine whose wrapped derived-type LHS has
`intent(out)` or `intent(inout)` and whose RHS has `intent(in)`. Unsafe or
unsupported forms are readiness blockers.

## Visibility And Names

`@private` marks classes, functions and methods private:

```python
@private
def helper(x: Int32) -> None: ...
```

`private[T]` marks a variable or argument private:

```python
hidden_value: private[Float64]
def consume(value: private[Int32]) -> None: ...
```

Names that are not valid Python identifiers are represented with `var[...]` for
data declarations, or with `Annotated[..., Name("native-name")]` for callable
arguments:

```python
var["class"]: Int32
def f(class_: Annotated[Int32, Name("class")]) -> None: ...
```

## Projection Metadata

`@native_call` is loaded and printed as projection metadata for edited stubs
whose Python-visible signature intentionally differs from the exact native
signature:

```python
@native_call([Arg(0), Arg(0).shape[0], Return(0)])
def normalize(values: Float64[:]) -> Float64: ...
```

Loaded projection entries:

| Entry | Meaning |
| --- | --- |
| `Arg(i)` | native argument is Python argument `i` |
| `Return(i)` | native argument is supplied by projected return slot `i` |
| `Const(value)` | hidden native literal |
| `Len(Arg(i))`, `Len(Return(i))`, `Len(Work("name"))` | hidden native length metadata |
| `Arg(i).shape[d]`, `Return(i).shape[d]`, `Work("name").shape[d]` | hidden native shape metadata |
| `IsPresent(Arg(i))` | hidden native optional-presence metadata |
| `Work("name")` | hidden workspace value |

This syntax is metadata today. Runtime lowering, allocation, copy-back,
validation, coercions and ownership behavior are roadmap work unless a backend
explicitly implements them.

## Current Generated Coverage

Generated `.pyi` currently covers these exact-contract areas:

| Area | Generated behavior |
| --- | --- |
| Fortran intrinsic scalars | compiler-aware semantic dtype names |
| C primitive scalars | compiler-probed semantic dtype names when a target report is supplied |
| Functions/subroutines | exact native argument order and direct return type |
| Fortran scalar references | `Ptr(Const(T))`, `Ptr(T)`, `Intent("out")` |
| Arrays | shaped storage with extents, strided axes, `ORDER_F` for multidimensional Fortran arrays |
| Constants | `Final[T]` module variables |
| C enums | open `Enum[T]` class plus module-level enumerators |
| Fortran derived types | classes with fields and methods when resolvable |
| Fortran generic interfaces | explicit `@overload("specific")` links with C-extension dtype/rank dispatch |
| Fortran defined operators | Python data-model methods plus explicit named-operator methods |
| Fortran defined assignment | explicit mutating `assign(...)` overloads |
| C structs/unions | `CStruct` and `CUnion` classes |
| C anonymous aggregate members | nested `CAnonymous` classes plus `CAnonymousMember` fields |
| Opaque types | `Opaque` classes and owner-module dependency stubs |
| Imports | `import ...` and `from ... import ...` with aliases |
| Incomplete C callbacks | placeholder type that readiness reports as incomplete |

Loaded but usually not generated from source today:

| Area | Loaded behavior |
| --- | --- |
| `Callable[[...], ...]` | complete callback/procedure signature metadata |
| `Ptr[n](T)` for `n > 1` | direct low-level pointer topology |
| `ORDER_ANY` | edited orientation-independent array contract |
| generic `Annotated` constraints | preserved semantic constraints |
| `@native_call` and `Returns[...]` | projection metadata |
| source-provenance array helpers | compatibility loading for older or edited stubs |

## Rejected Or Not Yet Supported

The loader intentionally rejects syntax that would be ambiguous or stale:

- `Unknown` semantic types.
- `Constant` or `Shape` as `Annotated` metadata.
- non-dimensional subscriptions such as `Float64[ORDER_F]`.
- `Ptr[1](T)`.
- untyped callable parameters.
- positional-only, keyword-only, vararg or kwarg function parameters.
- nested enum declarations.
- ordinary function bodies instead of `...`.
- unsupported decorators other than `@private`, `@native_call`,
  `@overload("specific")`, its documented `generic=` form, and
  `@staticmethod`.
- bare `@overload` or `typing.overload`; overload links require one concrete
  procedure name.

## Roadmap

Near-term format work:

1. Make C and Fortran callbacks/procedure pointers first-class by preserving
   complete `Callable[[...], ...]` contracts from source.
2. Add explicit pointer ownership, borrow, nullability, output-buffer and
   copy/readback policy so pointer-heavy C APIs can move beyond blockers.
3. Strengthen Fortran `character(len=...)` with length, kind, hidden-length ABI
   and `bind(c)` byte-string metadata.
4. Expand aggregate layout metadata for C bitfields, C attributes, Fortran
   `bind(c)`, `sequence`, and by-value aggregate ABI checks.
5. Represent Fortran polymorphic `class(...)` and procedure bindings without
   losing dynamic-type or dispatch information.

Projection/runtime roadmap:

1. Lower `@native_call` mappings into executable wrapper calls.
2. Add validation and coercion contracts for dtype, rank, shape, order,
   strides, alignment, mutability and aliasing.
3. Add ownership and lifetime contracts for opaque handles, pointer returns,
   allocatable/pointer reassociation, callbacks and work buffers.
4. Decide how to emit clean IDE/type-checker stubs from semantic `.pyi` files
   without losing the native wrapper contract.
