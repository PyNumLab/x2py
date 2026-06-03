# User Documentation

This page is for using x2py from the command line, from Python, or by editing
generated `.pyi` files. It avoids maintainer-only fixture and implementation
workflow details. For implementation and testing workflow, use
[developer.md](developer.md).

## What x2py Produces

x2py has four user-facing stages:

- Parse source and report parser facts.
- Convert parser facts to semantic IR.
- Generate editable `.pyi` semantic interface files.
- Check whether the semantic interface has enough information for wrapping.

The parser is intentionally wrapper-focused. It records declarations,
signatures, types, array and pointer facts, source locations, and diagnostics.
It does not infer ownership, callback lifetime, ABI shims, or Pythonic
projections unless the user supplies that policy in `.pyi`.

## Mental Model

Think of x2py as a staged pipeline:

```text
native source
  -> parser facts
  -> semantic IR
  -> editable `.pyi`
  -> readiness report
  -> future wrapper generation
```

Each stage has a different job:

- **Parser facts** are source-faithful. They preserve declarations,
  signatures, source locations, includes/imports, diagnostics, and native type
  facts.
- **Semantic IR** is language-neutral. C and Fortran declarations become the
  same semantic concepts: modules, functions, classes, variables, scalar
  types, arrays, pointers, constants, and blockers.
- **`.pyi`** is the editable user contract. It is where users can add missing
  policy that source code alone cannot prove.
- **Readiness** checks whether the semantic contract is complete enough to
  wrap. It reports blockers rather than guessing.
- **Wrapper generation** is the later stage that will consume a ready semantic
  contract.

The main rule is: generated `.pyi` files describe exact native contracts unless
you explicitly edit them. x2py should not silently hide native pointer/size
arguments, infer ownership, or invent callback lifetime policy.

## Main CLI Workflows

Parse Fortran:

```bash
python -m x2py path/to/file.f90 --parse
```

Parse C explicitly:

```bash
python -m x2py path/to/header.h --language c --parse
```

Generate semantic IR:

```bash
python -m x2py path/to/file.f90 --semantics
python -m x2py path/to/header.h --language c --semantics
```

Generate editable `.pyi` stubs:

```bash
python -m x2py path/to/file.f90 --pyi
python -m x2py path/to/header.h --language c --pyi
```

Write output beside the source or to an explicit file:

```bash
python -m x2py path/to/file.f90 --pyi --out
python -m x2py path/to/file.f90 --pyi --out interface.pyi
```

Check wrap readiness:

```bash
python -m x2py path/to/file.f90 --wrap-readiness
python -m x2py path/to/interface.pyi --wrap-readiness
```

When a generated `.pyi` file needs policy that the parser cannot infer, edit
the stub and run readiness on the edited file. The edited `.pyi` is the
user-visible semantic contract.

## End-To-End Tutorial

This tutorial uses checked repository fixtures so the commands are easy to
reproduce from the project root.

### 1. Parse A Fortran Source

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
```

Expected output shape:

```text
File: tests/data/fortran/general/basic_subroutine.f90
  Modules: 1
    - module m1 (vars=0, uses=0)
      Procedures: 1
        - subroutine add1(n:integer[0], x:real(8)[1])
```

The parser is reporting native source facts only: modules, variables, procedure
signatures, argument types, ranks, and source diagnostics.

### 2. Convert To Semantic IR

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --semantics
```

Semantic output is the language-neutral view consumed by readiness and `.pyi`
generation. Use this when you need machine-readable contract data rather than
a human parse tree.

### 3. Generate An Editable `.pyi`

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
```

Generated stubs preserve the exact native interface. For example, scalar
Fortran dummy arguments without `value` appear as `Ptr(...)`, and arrays appear
with their storage contract:

```python
def add1(
    n: Ptr(Const(Int32)),
    x: Float64[n]
) -> None: ...
```

If the generated file is complete, you can use it as-is. If readiness reports
missing policy, edit the `.pyi` and make the contract explicit.

### 4. Check Readiness

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
```

For scripting, use JSON:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness --json
```

Look at `wrappable`, `wrappability_blockers`, `unit_blockers`, and
`why_not_wrappable`.

### 5. Edit `.pyi` When Source Is Not Enough

Some native APIs need user policy. For example, a C callback API may parse
successfully, but readiness may require a `Callable[...]` contract:

```python
from typing import Callable

def walk_items(
    items: Ptr(Any),
    visit: Callable[[Ptr(Any), Ptr(Any)], None],
    userdata: Ptr(Any),
) -> None: ...
```

After editing, run readiness on the `.pyi` file:

```bash
python -m x2py path/to/interface.pyi --wrap-readiness
```

## Python API Workflows

Parse one Fortran file:

```python
from x2py import parse_fortran_file

parsed = parse_fortran_file("path/to/file.f90")
print([module.name for module in parsed.modules])
```

Parse one C snippet or raw C file:

```python
from x2py import parse_c_file

parsed = parse_c_file("int add(int a, int b);", filename="api.h")
print([function.name for function in parsed.functions])
```

Parse a C project explicitly:

```python
from x2py import parse_c_project

project = parse_c_project(["src/api.c", "include/api.h"], include_dirs=["include"])
print(project.include_graph)
```

Generate semantic IR and assess readiness:

```python
from x2py import (
    assess_semantic_wrap_readiness,
    fortran_file_to_semantic_modules,
    parse_fortran_file,
)

parsed = parse_fortran_file("path/to/file.f90")
modules = fortran_file_to_semantic_modules(parsed, standalone_module_name="file")
report = assess_semantic_wrap_readiness(modules, source="path/to/file.f90")
print(report["wrappable"])
```

## `.pyi` File Format

x2py `.pyi` files are Python-valid semantic interface files. They describe the
native interface that x2py should wrap. Generated stubs are exact native
contracts by default: they do not hide pointer arguments, reorder arguments, or
turn output arguments into Python return values unless the `.pyi` explicitly
does that.

### Scalars

Bare scalar types are direct values:

```python
def dot_value(a: Float64, b: Float64) -> Float64: ...
```

Fortran scalar dummy arguments without `value` and C pointer-like scalar
storage are explicit pointer/reference contracts:

```python
def inspect(value: Ptr(Const(Int32))) -> None: ...
def update(value: Ptr(Float64)) -> None: ...
```

`Ptr(Const(T))` means the native side receives a pointer/reference to read-only
storage. `Ptr(T)` means writable storage.

### Arrays

Array storage uses NumPy-style subscriptions:

```python
def scale(n: Ptr(Const(Int32)), x: Float64[n]) -> None: ...
def dot3(a: Const(Float64[3]), b: Const(Float64[3])) -> Float64: ...
```

Multidimensional Fortran-oriented storage uses `Annotated[..., ORDER_F]`:

```python
def fill_identity3(
    a: Annotated[Float64[3, 3], ORDER_F, Intent("out")]
) -> None: ...
```

Stride-aware arrays use slice syntax:

```python
def scale_vector(v: Float64[::Strided], alpha: Ptr(Const(Float64))) -> None: ...
def update_matrix(a: Annotated[Float64[::Strided, ::Strided], ORDER_F]) -> None: ...
```

Rank-one arrays do not need an order marker. Multidimensional arrays default to
C order unless `ORDER_F` or `ORDER_ANY` is written.

### Constants And Globals

Constants use `Final[...]`:

```python
answer: Final[Int32] = 42
pi: Final[Float64]
```

Module variables and global variables use normal annotations:

```python
counter: Int32
weights: Float64[16]
```

### Classes And Opaque Handles

Derived types, structs, and opaque native handles are represented as classes:

```python
class particle:
    id: Int32
    mass: Float64
    position: Float64[3]
```

Opaque handles can be declared without exposing native layout:

```python
class context(Opaque):
    pass

def context_destroy(ctx: Ptr(context)) -> None: ...
```

### Intent, Allocatable, And Pointer Metadata

Use `Annotated[...]` for non-dimensional metadata:

```python
def fill(x: Annotated[Float64[:], Intent("out")]) -> None: ...
value: Annotated[Float64[:], ORDER_F, Allocatable]
view: Annotated[Float64[:], ORDER_F, Pointer]
```

`Intent("out")` is emitted when the exact native argument is an output
argument. For `intent(inout)`, the writable type itself normally carries the
contract.

### Callback Policy

If the parser finds a callback shape but cannot prove its policy, edit the
stub with a `Callable[...]` signature:

```python
from typing import Callable

def walk_items(
    items: Ptr(Any),
    visit: Callable[[Ptr(Any), Ptr(Any)], None],
    userdata: Ptr(Any),
) -> None: ...
```

The signature tells x2py the callable argument and return contract. Ownership,
lifetime, threading, and registration/unregistration policy still need to be
explicit when wrapper generation reaches those cases.

### Pythonic Projections With `@native_call`

The exact native form keeps every native argument visible:

```python
def add(
    a: Float64,
    b: Float64,
    c: Annotated[Ptr(Float64), Intent("out")]
) -> None: ...
```

A projected form can use `@native_call` to say how the Python signature maps to
native arguments:

```python
@native_call([Arg(0), Arg(1), Return(0)])
def add(a: Float64, b: Float64) -> Float64: ...
```

Here, native argument 0 comes from Python argument 0, native argument 1 comes
from Python argument 1, and native argument 2 is represented as Python return
value 0. Use projections only when you are intentionally changing the
Python-visible contract. Without explicit projection metadata, x2py keeps the
native contract.

## Datatype Mapping

These are the stable semantic names used in generated `.pyi` files and
readiness checks.

| Semantic dtype | NumPy equivalent | Typical source spellings |
| --- | --- | --- |
| `Bool` | `numpy.bool_` | Fortran `logical`, C `_Bool` |
| `Int8` | `numpy.int8` | `integer(kind=1)`, `signed char`, `int8_t` |
| `Int16` | `numpy.int16` | `integer(kind=2)`, `short`, `int16_t` |
| `Int32` | `numpy.int32` | `integer`, `integer(c_int)`, `int`, `int32_t` |
| `Int64` | `numpy.int64` | `integer(kind=8)`, `long`, `long long`, `int64_t` |
| `UInt8` | `numpy.uint8` | `unsigned char`, `uint8_t` |
| `UInt16` | `numpy.uint16` | `unsigned short`, `uint16_t` |
| `UInt32` | `numpy.uint32` | `unsigned int`, `uint32_t` |
| `UInt64` | `numpy.uint64` | `unsigned long`, `unsigned long long`, `uint64_t` |
| `Float32` | `numpy.float32` | `real(kind=4)`, `real(c_float)`, `float` |
| `Float64` | `numpy.float64` | `real`, `real(kind=8)`, `real(c_double)`, `double` |
| `Float128` | `numpy.longdouble` | `real(kind=16)`, `long double` |
| `Complex64` | `numpy.complex64` | `complex(kind=4)`, `float _Complex` |
| `Complex128` | `numpy.complex128` | `complex`, `complex(kind=8)`, `double _Complex` |
| `Complex256` | `numpy.clongdouble` | `complex(kind=16)`, `long double _Complex` |
| `String` | `numpy.str_` or ABI byte storage | Fortran `character`, C `char *` policy |
| `SizeT` | `numpy.uintp` or probed unsigned width | C `size_t` |
| `Any` | `object` | `void *` pointees or intentionally opaque values |

C standard-library typedefs such as `size_t`, `time_t`, and `FILE` can depend
on the target compiler and headers. Use the compiler/type probes when target
ABI precision matters.

## Examples

### Fortran Exact Stub

Fortran source:

```fortran
subroutine update(scale, value, result)
  real(8), value, intent(in) :: scale
  real(8), intent(inout) :: value
  real(8), intent(out) :: result
end subroutine
```

Generated exact `.pyi` shape:

```python
def update(
    scale: Float64,
    value: Ptr(Float64),
    result: Annotated[Ptr(Float64), Intent("out")]
) -> None: ...
```

### Fortran Array Stub

Fortran source:

```fortran
subroutine fill_identity3(a)
  real(8), intent(out) :: a(3, 3)
end subroutine
```

Generated `.pyi` shape:

```python
def fill_identity3(
    a: Annotated[Float64[3, 3], ORDER_F, Intent("out")]
) -> None: ...
```

### C Exact Stub

C header:

```c
int scale_values(size_t n, double values[n]);
double dot3(const double a[3], const double b[3]);
```

Generated `.pyi` shape for the supported exact subset:

```python
def scale_values(n: SizeT, values: Float64[n]) -> Int32: ...
def dot3(a: Const(Float64[3]), b: Const(Float64[3])) -> Float64: ...
```

If x2py cannot prove the pointer/array relationship, readiness reports a
blocker instead of inventing a contract.

### Opaque Handle Stub

C header:

```c
struct context;
struct context *context_create(void);
void context_destroy(struct context *ctx);
```

Generated `.pyi` shape:

```python
class context(Opaque):
    pass

def context_create() -> Ptr(context): ...
def context_destroy(ctx: Ptr(context)) -> None: ...
```

## Readiness Reports

Readiness answers whether the semantic interface is complete enough to wrap.
Use JSON output when scripting:

```bash
python -m x2py path/to/interface.pyi --wrap-readiness --json
```

Important fields include:

- `wrappable`: final file-level answer.
- `n_modules`, `n_functions`, `n_classes`, `n_variables`: public API counts.
- `wrappability_blockers`: all blockers.
- `unit_blockers`: blockers grouped by function/class/module/global owner.
- `why_not_wrappable`: human-oriented blocker messages.

Common blockers:

- unresolved semantic types;
- missing compile-time values;
- unresolved shape symbols;
- ambiguous C pointer ownership;
- unsupported variadic functions;
- incomplete callback policy;
- unsupported unions or ABI-sensitive fields.

When a blocker is policy-related, edit the `.pyi` to provide the missing
contract and rerun readiness.

## User Responsibilities And Limits

x2py deliberately avoids guessing policy that can change memory safety or API
meaning. Users should expect to provide policy for:

- **Pointer ownership:** whether `T *` is borrowed, owned, nullable, mutable,
  a scalar reference, or array storage.
- **Pointer/size relationships:** which `n`, `len`, `capacity`, or shape
  argument describes which pointer.
- **Output buffers:** whether an output pointer remains a native argument or
  becomes a Python return value through `@native_call`.
- **Callbacks:** callable signature, lifetime, context/userdata pairing,
  registration/unregistration, threading, and exception policy.
- **ABI-sensitive structs/unions/bitfields:** whether direct passing is safe,
  blocked, or needs a generated shim.
- **Compiler-dependent typedefs:** target-specific widths for types such as
  `size_t`, `time_t`, and library handles.
- **Macro configurations:** parse each compiler-selected configuration after
  preprocessing; do not expect raw macro expansion inside the parser.

These limits are intentional. A readiness blocker is a request for a clearer
semantic contract, not just a parser failure.

## Verified Example Sources

These repository files and tests are useful examples to run or inspect:

- Fortran user flow:
  `tests/data/fortran/general/basic_subroutine.f90`
- Rich generated `.pyi` snapshot:
  `tests/data/fortran/general/modern_pyi_example.f90` and
  `tests/semantics/test_pyi_printer_modern_example.py`
- Edited `.pyi` syntax and `@native_call` examples:
  `tests/pyi/test_pyi_to_ir.py`
- C parser and semantic examples:
  `tests/data/c/general/math_api.h` and `tests/semantics/test_c2ir.py`
- Readiness examples:
  `tests/semantics/test_semantic_wrap_readiness.py` and
  `tests/semantics/test_c_semantic_readiness.py`

## More Detail

Use [semantics.md](semantics.md) for the full `.pyi` and semantic reference.
Use [diagnostic_codes.md](diagnostic_codes.md) for stable diagnostic code
names. Use [developer.md](developer.md) only when changing x2py itself.
