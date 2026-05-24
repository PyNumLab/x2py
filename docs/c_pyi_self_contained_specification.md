# Self-Contained C Semantic `.pyi` Implementation Specification

**Status:** Phase 1 implementation baseline
**Target:** Python wrappers for C libraries on a selected Linux ABI
**Primary requirement:** A semantic `.pyi` file plus a compiled library is
sufficient to generate a wrapper. C header parsing is optional input
generation, not a wrapper-generation dependency.

## 1. Phase 1 Boundary

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

## 2. Non-Negotiable Rules

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
6. Numeric one-level pointers use NumPy storage notation:
   `T[()]` for zero-dimensional storage and `T[dimensions...]` for array
   storage. Both lower to one native `T *`.
7. Array dimensions express validation constraints, not additional pointer
   depth. `Float64[:, :]` still lowers to one `double *`, never `double **`.
8. With no stride or order modifier, numeric array storage is C-contiguous.
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

## 3. Current Artifact

The current compiler-facing artifact is:

```text
module.x2py.pyi
```

It may use x2py semantic types, but it contains only identity-callable
functions in Phase 1.

A clean `.pyi` for standard type checkers is not part of Phase 1.

## 4. Scalar Types Passed By Value

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

## 5. Numeric Pointer Storage

### 5.1 Canonical NumPy Notation

A numeric NumPy storage annotation means the caller supplies memory whose data
address is passed directly to C.

| Semantic annotation | Python caller supplies | Native parameter |
| --- | --- | --- |
| `Int[()]` | writable zero-dimensional NumPy array with C `int` dtype | `int *` |
| `Const(Int[()])` | matching NumPy scalar or zero-dimensional storage | `const int *` |
| `Int[:]` | writable one-dimensional C-contiguous NumPy array | `int *` |
| `Const(Int[:])` | read-only one-dimensional C-contiguous NumPy array | `const int *` |
| `Float64[:]` | writable one-dimensional C-contiguous NumPy array | `double *` |
| `Const(Float64[:])` | read-only one-dimensional C-contiguous NumPy array | `const double *` |
| `Float64[0:n]` | writable one-dimensional array whose extent is validated against visible argument `n` | `double *` |
| `Const(Float64[0:n])` | read-only one-dimensional array whose extent is validated against visible argument `n` | `const double *` |
| `Float64[:, :]` | writable rank-two C-contiguous NumPy array | `double *` |
| `Float64[3, 4]` | writable C-contiguous NumPy array with exact shape `(3, 4)` | `double *` |

`T[()]` and `T[dimensions...]` are the only current spelling for ordinary
NumPy-backed numeric pointer parameters. Do not also write `Ptr(...)`.

### 5.2 Direct Pointer Objects

Some native parameters are pointers but are not ordinary one-level numeric
storage. Their exact identity representation uses the canonical pointer
constructor:

| Semantic annotation | Native parameter |
| --- | --- |
| `Ptr(T)` | `T *` direct low-level pointer object |
| `Ptr(Const(T))` | `const T *` direct low-level pointer object |
| `Ptr[2](T)` | `T **` direct low-level pointer object |
| `Ptr[2](Const(T))` | `const T **` direct low-level pointer object |
| `Ptr[n](T)` | `T` followed by exactly `n` native pointer layers, `n >= 2` |

`Ptr(x)` is the only canonical depth-one spelling. `Ptr[1](x)` is invalid.

For ordinary numeric `int *`/`double *` inputs whose scalar or array storage
contract is known, use the NumPy forms instead of `Ptr(Int)` or
`Ptr(Float64)`. `Ptr[n](T)` is necessary for native pointer graphs and for
low-level pointer values that are not represented by a NumPy storage
contract.

A direct pointer object carries a typed native address. Passing or returning
it does not imply allocation, copying, ownership or automatic destruction.
For example, a raw pointer returned by one native function can be passed to a
second native function under matching `Ptr(...)` annotations. Pointer-object
construction/allocation helpers are runtime API work, not additional
information required in a semantic function signature.

### 5.3 Pointer To Scalar

```c
void increment(int *value);
void read_count(const int *value);
```

Phase 1 interface:

```python
def increment(value: Int[()]) -> None: ...
def read_count(value: Const(Int[()])) -> None: ...
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

### 5.4 Pointer To Array

```c
void negate(int n, double *values);
double sum_values(size_t n, const double *values);
```

Phase 1 interface:

```python
def negate(n: Int, values: Float64[0:n]) -> None: ...
def sum_values(n: SizeT, values: Const(Float64[0:n])) -> Float64: ...
```

The caller supplies `n` explicitly because it is an actual C parameter. The
wrapper must not derive it from `len(values)` in Phase 1.

### 5.5 Output Pointer Remains An Argument

```c
void get_count(int *out);
void get_values(int n, double *out);
```

Phase 1 interface:

```python
def get_count(out: Int[()]) -> None: ...
def get_values(n: Int, out: Float64[0:n]) -> None: ...
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
`Float64[0:n]` from `get_values(n)` is a later Pythonic adaptation, not an
identity call.

## 6. Array Constraints

### 6.1 Rank And Fixed Dimensions

Dimensions refine valid NumPy storage while the native argument remains one
data pointer.

```c
void process_matrix(double *matrix);
void use_row(int (*row)[4]);
void use_matrix(int (*matrix)[4]);
```

```python
def process_matrix(matrix: Float64[:, :]) -> None: ...
def use_row(row: Int[4]) -> None: ...
def use_matrix(matrix: Int[:, 4]) -> None: ...
```

- `Float64[:, :]` validates rank two and C contiguity, then passes one
  `double *`.
- `Int[4]` validates one fixed row of four `int` values, then passes one
  address.
- `Int[:, 4]` validates contiguous rows of fixed width four, then passes one
  address.

For function parameters on the selected ABI, `int (*)[4]` is represented as
one pointer plus its fixed row-width contract. It is not represented as
`int **`.

### 6.2 Pointer Graphs Are Different

```c
void use_rows(int **rows);
void update_value(int *****value);
```

Neither declaration is represented by `Int[:, :]`. NumPy array notation
supplies one contiguous data pointer only. Their exact low-level Phase 1
interfaces are:

```python
def use_rows(rows: Ptr[2](Int)) -> None: ...
def update_value(value: Ptr[5](Int)) -> None: ...
```

The caller supplies an x2py-compatible native pointer object with the declared
topology. The wrapper passes it unchanged. Constructing pointer rows from
nested Python sequences and exposing `update_value(value: Int) -> Int` are
later Pythonic adaptations.

### 6.3 Contiguity

Phase 1 accepts only C-contiguous numeric arrays for `T[:]`, `T[:, :]`,
fixed-dimension forms and dependent dimension forms such as `T[0:n]`.
Dependent dimensions may reference visible scalar arguments only; they
validate storage and do not generate or change native arguments. Strided
inputs, Fortran-order inputs, automatic packing and copy-back are deferred.

## 7. Direct Native Returns

### 7.1 Scalars And `void`

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

### 7.2 Pointer Returns

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
    Float64[0:n],
    Owned,
    FreeWith("free_values"),
]: ...
```

This does not require `@native_call` because the C function directly returns
the pointer represented by the Python return annotation. Until shape and
lifetime handling are implemented, return it as the corresponding direct
low-level pointer object or reject the higher-level NumPy view rather than
guessing.

## 8. Symbol Names

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
def increment(value: Int[()]) -> None: ...
```

`@bind` changes only which exported symbol is loaded. It does not synthesize
arguments, change pointers or alter results.

## 9. Structures, Enums And Non-Numeric Pointers

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

## 10. Phase 1 Unsupported Transformations

Phase 1 must reject, or leave unresolved during optional C import generation,
any interface that requires the wrapper to change the native function shape.

Unsupported now:

| Desired behavior | Example C shape | Later mechanism |
| --- | --- | --- |
| Pass a Python scalar through a native pointer | `void increment(int *value)` exposed as `value = increment(value)` | `@native_call(Ptr(Arg(0)))` plus readback |
| Generate a hidden length | `double sum(size_t n, const double *x)` exposed as `sum(x)` | `len(Arg(0))` in `@native_call` |
| Turn an output pointer into a Python result | `void get_count(int *out)` exposed as `get_count() -> Int` | `Return(...)` in `@native_call` |
| Convert native status to exception | `int create(...);` with hidden status | `Status[...]` and `Check(...)` |
| Wrap a raw opaque pointer with ownership behavior | `struct ctx *` / `struct ctx **` | handle and lifetime policy |
| Convert Python strings to C strings | `const char *` from `str` | text encoding/termination policy |
| Generate callback thunks | function-pointer argument | callback lifetime/exception policy |
| Pack or copy non-contiguous arrays | pointer to contiguous data | `Pack` / `CopyBack` coercions |

The later syntax is retained as design direction only. It is not required by
the Phase 1 parser, IR, printer or wrapper generator.

## 11. Required Phase 1 Readiness Errors

The wrapper generator or optional importer must report unsupported behavior
instead of silently changing the interface.

| Code | Condition |
| --- | --- |
| `c_non_identity_call_unsupported` | A declaration or semantic interface requires synthesized, omitted, reordered or transformed parameters/results. |
| `c_pointer_object_mismatch` | A `Ptr(T)` or `Ptr[n](T)` parameter is supplied a value without the declared direct native pointer topology. |
| `c_numpy_pointer_return_policy_required` | A native pointer return is exposed as a shaped NumPy result without implemented lifetime handling or explicit required metadata; a direct raw `Ptr(T)` return remains identity behavior. |
| `c_numpy_dtype_mismatch` | Supplied NumPy storage does not have the exact semantic native element dtype. |
| `c_numpy_rank_mismatch` | Supplied NumPy storage does not satisfy declared zero-dimensional, rank or fixed-shape constraints. |
| `c_numpy_contiguity_required` | Supplied numeric array is not C-contiguous. |
| `c_numpy_writeability_required` | A mutable native pointer receives read-only NumPy storage. |
| `c_opaque_handle_conversion_unsupported` | A raw opaque pointer is requested as an owning/high-level Python handle rather than direct `Ptr(context)` identity. |
| `c_string_conversion_unsupported` | A Python string conversion is requested. |
| `c_callback_unsupported` | A Python callback-to-native-function-pointer mapping is requested. |
| `c_union_unsupported` | A callable interface includes an unsupported union. |
| `c_variadic_function_unsupported` | A variadic native function is requested. |
| `c_calling_convention_unsupported` | A non-default calling convention is required. |

## 12. Phase 1 Parser And Wrapper Requirements

The Phase 1 implementation must:

1. Parse scalar annotations and direct `None`/scalar return annotations.
2. Parse numeric NumPy storage forms:
   `T[()]`, `Const(T[()])`, `T[:]`, `Const(T[:])`, `T[:, :]` and fixed
   integer dimensions such as `T[3, 4]`, plus dependent dimensions such as
   `T[0:n]` referencing a visible scalar parameter.
3. Lower each supported pointer-backed numeric annotation to exactly one
   native pointer of its leaf type.
4. Parse and lower direct pointer forms `Ptr(T)` and `Ptr[n](T)` as exactly
   one and `n` native pointer layers, and accept only compatible low-level
   native pointer objects at runtime.
5. Validate NumPy dtype, rank, fixed dimensions, C contiguity and
   writeability before calling native code.
6. Preserve the visible parameter order exactly.
7. Preserve direct native scalar, pointer and native `void` returns.
8. Parse and apply `@bind("symbol")` for identity symbol renaming.
9. Parse complete by-value `Structure`, `Enum[T]` and opaque pointer leaf
   declarations if those existing declaration features are already runnable;
   otherwise report them as not yet supported without approximating them.
10. Reject `@native_call`, `Arg`, `Return`, `Returns`, `Status`, `Check`,
   `Pack`, `CopyBack` and callback conversion constructs as later-phase
   syntax if encountered in a Phase 1 runnable input.
11. Never consult C source after a supported semantic `.pyi` has been parsed.

## 13. Phase 1 Tests

### 13.1 By-Value Scalar Identity

```c
int add(int a, int b);
```

```python
def add(a: Int, b: Int) -> Int: ...
```

The wrapper passes two native `int` values and returns one native `int`.

### 13.2 Mutable Scalar Pointer Storage

```c
void increment(int *value);
```

```python
def increment(value: Int[()]) -> None: ...
```

Tests must verify that a writable zero-dimensional NumPy array is passed by
data address and that native mutation is observed after the call. A plain
Python `int` must be rejected for this signature.

### 13.3 Read-Only Scalar Pointer Storage

```c
void read_count(const int *value);
```

```python
def read_count(value: Const(Int[()])) -> None: ...
```

Tests must verify matching scalar storage/input acceptance and exact native
pointer lowering without writable requirements.

### 13.4 Array Pointer With Explicit Count

```c
double sum_values(size_t n, const double *values);
```

```python
def sum_values(n: SizeT, values: Const(Float64[0:n])) -> Float64: ...
```

Tests must verify that the caller passes `n`, that the wrapper passes it
unchanged, and that no hidden `len(values)` argument is generated.

### 13.5 Explicit Output Storage

```c
void get_count(int *out);
void get_values(int n, double *out);
```

```python
def get_count(out: Int[()]) -> None: ...
def get_values(n: Int, out: Float64[0:n]) -> None: ...
```

Tests must verify mutation of caller-allocated output storage and that the
functions return `None`.

### 13.6 Matrices And Pointer-To-Fixed-Array

```c
void matrix_data(double *matrix);
void matrix_rows(int (*matrix)[4]);
```

```python
def matrix_data(matrix: Float64[:, :]) -> None: ...
def matrix_rows(matrix: Int[:, 4]) -> None: ...
```

Tests must verify one native pointer argument for each function, rank/shape
validation, and rejection of a representation treating either argument as
`T **`.

### 13.7 Direct Pointer Graph Identity

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

### 13.8 Raw Opaque Pointer Identity

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

### 13.9 Symbol Binding Without Transformation

```c
int library_add(int a, int b);
```

```python
@bind("library_add")
def add(a: Int, b: Int) -> Int: ...
```

Tests must verify that `@bind` changes symbol lookup only and leaves
argument/return lowering unchanged.

### 13.10 Transformation Is Not Phase 1

The Phase 1 parser or readiness checker must reject a runnable interface using
later transformation syntax such as:

```python
@native_call(Ptr(Arg(0)))
def increment(value: Int) -> Returns["value", Int]: ...
```

The supported Phase 1 spelling for the same C function is:

```python
def increment(value: Int[()]) -> None: ...
```

## 14. Phase 2: Pythonic Adaptations After Identity Works

After Phase 1 can call direct signatures reliably, `@native_call` introduces
Python-facing APIs that differ from their C parameter lists. The settled
design direction is:

```python
# C: void increment(int *value);
@native_call(Ptr(Arg(0)))
def increment_value(value: Int) -> Returns["value", Int]: ...

# C: double sum_values(size_t n, const double *values);
@native_call(As[SizeT](len(Arg(0))), Arg(0), returns=Return(0))
def sum_values(values: Const(Float64[:])) -> Float64: ...

# C: void get_values(int n, double *out);
@native_call(Arg(0), Return(0))
def get_values(n: Int) -> Float64[0:n]: ...

# C: int context_create(struct context **out);
@native_call(
    Ptr(Return(0)),
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
- derived arguments such as `len(Arg(i))`, `.shape[...]`, `.size` and
  `.step`.

None of these transformations is necessary to complete Phase 1.

## 15. Decisions Deferred Beyond Phase 1

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
6. Strided/Fortran-order storage, packing and copy-back.
7. Clean generated `.pyi` files for IDEs and type checkers.
8. Module/library selection, platform variants and non-default calling
   conventions.
9. Unions, writable native globals and variadic functions.

No deferred behavior may be silently inferred by the Phase 1 wrapper
generator.
