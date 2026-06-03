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

x2py uses the same stage flags for Fortran and C:

- `--parse` prints parser facts.
- `--semantics` prints language-neutral semantic IR.
- `--pyi` prints editable `.pyi` interface text.
- `--wrap-readiness` checks whether the semantic contract is complete enough
  for wrapping.

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

## Example Input Files

The command examples below use these checked repository fixtures. Reading the
source, command, and output together should make each parser result
reproducible from the project root.

`tests/data/fortran/general/basic_subroutine.f90`

```fortran
module m1
contains
subroutine add1(n, x)
  integer, intent(in) :: n
  real(kind=8), intent(inout), dimension(n) :: x
end subroutine add1
end module m1
```

`tests/data/c/general/math_api.h`

```c
#ifndef X2PY_GENERAL_MATH_API_H
#define X2PY_GENERAL_MATH_API_H

double norm2(int n, const double x[static 1]);
void scale(int n, double alpha, double x[static 1]);
double dot(int n, const double *restrict x, const double *restrict y);
void fill_identity3(double a[static 3][3]);

#endif
```

## Compiler-Backed CLI Examples

The CLI path uses compiler preprocessing for source parsing. C defaults to
`cc`, and Fortran defaults to `gfortran`, but wrapper work should pass the
same compiler and target flags used by the native project.

### C With Include Paths, Macros, And Standard

This command parses the `math_api.h` header shown in
[Example Input Files](#example-input-files):

```bash
python -m x2py tests/data/c/general/math_api.h --language c --parse --json \
  --compiler cc \
  -I tests/data/c/general \
  -D API_EXPORT= \
  --std c11
```

The output is full parser JSON. The abbreviated excerpt below shows the
top-level fields that prove the file was compiler-preprocessed and which
recipe was used:

```json
{
  "tests/data/c/general/math_api.h": {
    "filename": "tests/data/c/general/math_api.h",
    "language": "c",
    "preprocessing": "compiler",
    "preprocessing_recipe": {
      "compiler": "cc",
      "adapter": "gcc-compatible-c",
      "argv": ["cc", "-E", "-x", "c", "-Itests/data/c/general", "-DAPI_EXPORT=", "-std=c11", "..."],
      "include_dirs": ["tests/data/c/general"],
      "defines": ["API_EXPORT="],
      "standard": "c11",
      "included_files": [{"path": "tests/data/c/general/math_api.h", "exposure": "public"}]
    },
    "functions": [{"name": "norm2"}, {"name": "scale"}, {"name": "dot"}, {"name": "fill_identity3"}],
    "diagnostics": []
  }
}
```

The same compiler flags flow through semantic, `.pyi`, and readiness stages:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --pyi \
  --compiler cc \
  -I tests/data/c/general \
  -D API_EXPORT= \
  --std c11
```

Expected `.pyi` output:

```python
File: tests/data/c/general/math_api.h
def norm2(
    n: Int32,
    x: Const(Float64[1])
) -> Float64: ...

def scale(
    n: Int32,
    alpha: Float64,
    x: Float64[1]
) -> None: ...

def dot(
    n: Int32,
    x: Ptr(Const(Float64)),
    y: Ptr(Const(Float64))
) -> Float64: ...

def fill_identity3(
    a: Float64[3, 3]
) -> None: ...
```

Readiness for the same fixture:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --wrap-readiness \
  --compiler cc \
  -I tests/data/c/general \
  -D API_EXPORT= \
  --std c11
```

```text
File: tests/data/c/general/math_api.h
  Source: c
  Semantic modules: math_api
  Wrappable: yes
  Public functions: 4
  Public classes: 0
  Public variables: 0
  No semantic readiness blockers detected.
```

### C With Project Flags From `compile_commands.json`

When a C project already has a compile database, use it so x2py sees the same
include paths, macros, target flags, and source language mode as the project:

```bash
python -m x2py src/api.c --language c --parse \
  --compile-commands build/compile_commands.json
```

If the database entry needs extra wrapper-specific flags, add them explicitly:

```bash
python -m x2py src/api.c --language c --semantics \
  --compile-commands build/compile_commands.json \
  --compiler-arg=--sysroot=/opt/sdk
```

### Fortran With Compiler Flags

Use explicit Fortran compiler mode when source depends on CPP macros,
predefined compiler behavior, include paths, or target kind flags:

This command parses the `basic_subroutine.f90` file shown in
[Example Input Files](#example-input-files):

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 \
  --language fortran \
  --parse --json \
  --compiler /usr/bin/gfortran \
  -I tests/data/fortran/general \
  -D USE_MPI \
  --std f2008 \
  --compiler-arg=-fdefault-real-8
```

The output is full parser JSON. The abbreviated excerpt below shows the same
recipe shape:

```json
{
  "tests/data/fortran/general/basic_subroutine.f90": {
    "modules": [{"name": "m1"}],
    "preprocessing_recipe": {
      "language": "fortran",
      "compiler": "/usr/bin/gfortran",
      "adapter": "gnu-fortran",
      "argv": ["/usr/bin/gfortran", "-E", "-cpp", "-Itests/data/fortran/general", "-DUSE_MPI", "-std=f2008", "-fdefault-real-8", "..."],
      "include_dirs": ["tests/data/fortran/general"],
      "defines": ["USE_MPI"],
      "standard": "f2008",
      "compiler_args": ["-fdefault-real-8"]
    }
  }
}
```

The same flags can generate `.pyi`:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 \
  --language fortran \
  --pyi \
  --compiler /usr/bin/gfortran \
  -I tests/data/fortran/general \
  -D USE_MPI \
  --std f2008 \
  --compiler-arg=-fdefault-real-8
```

```python
File: tests/data/fortran/general/basic_subroutine.f90
def add1(
    n: Ptr(Const(Int32)),
    x: Float64[n]
) -> None: ...
```

### Include Exposure

For C projects, included declarations can be public or private in the
wrapper-facing interface. By default, reachable project includes are public and
system headers are private. Use exposure flags when the public wrapper surface
should be narrower:

```bash
python -m x2py include/api.h --language c --pyi \
  --include-exposure roots-only \
  --public-include 'include/public/*' \
  --private-include 'vendor/*'
```

Private declarations remain available internally for type resolution. Public
signatures that refer to private handle types can still use opaque dependency
stubs rather than exposing private data members.

### Custom Preprocessor Adapter

For unsupported compiler families, provide a command template. Placeholders
are expanded by x2py:

```bash
python -m x2py path/to/api.h --language c --parse \
  --preprocessor-adapter command-template \
  --preprocess-template 'cc -E {include_dirs} {defines} {undefs} {standard} {compiler_args} {source}'
```

Supported placeholders include `{source}`, `{include_dirs}`, `{defines}`,
`{undefs}`, `{standard}`, and `{compiler_args}`.

## End-To-End Tutorial

This tutorial uses checked repository fixtures so the commands are easy to
reproduce from the project root. The Fortran steps use
`tests/data/fortran/general/basic_subroutine.f90`, shown in
[Example Input Files](#example-input-files).

### 1. Parse A Fortran Source

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
```

Expected output:

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
File: tests/data/fortran/general/basic_subroutine.f90
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

## C End-To-End Tutorial

Use explicit C mode for C headers and sources. These commands use
`tests/data/c/general/math_api.h`, shown in
[Example Input Files](#example-input-files):

```bash
python -m x2py tests/data/c/general/math_api.h --language c --parse
```

Expected parse output:

```text
File: tests/data/c/general/math_api.h
  Language: c
  Functions: 4
  Structs: 0
  Unions: 0
  Enums: 0
  Typedefs: 0
  Variables: 0
  Macros: 0
  Includes: 0
  Diagnostics: 0
```

Generate semantic IR JSON:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --semantics
```

The semantic payload contains `semantic_modules` and a generated `pyi` string.
The module metadata includes `source_language: c` and `preprocessing:
compiler`.

Generate `.pyi` directly:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --pyi
```

The output preserves exact native contracts for the supported subset:

```python
File: tests/data/c/general/math_api.h
def norm2(
    n: Int32,
    x: Const(Float64[1])
) -> Float64: ...

def scale(
    n: Int32,
    alpha: Float64,
    x: Float64[1]
) -> None: ...

def dot(
    n: Int32,
    x: Ptr(Const(Float64)),
    y: Ptr(Const(Float64))
) -> Float64: ...

def fill_identity3(
    a: Float64[3, 3]
) -> None: ...
```

Check readiness:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --wrap-readiness
```

```text
File: tests/data/c/general/math_api.h
  Source: c
  Semantic modules: math_api
  Wrappable: yes
  Public functions: 4
  Public classes: 0
  Public variables: 0
  No semantic readiness blockers detected.
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

The loader accepts ordinary imports used by the semantic file:

```python
from typing import Annotated, Callable, Final
from other_module import particle
```

Imports matter when generated stubs refer to owner-module dependency stubs or
when an edited file supplies callback types.

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

### Function Returns

A plain return type is a direct native return:

```python
def norm2(n: Int32, x: Const(Float64[1])) -> Float64: ...
```

Functions that return multiple Python values can use tuple syntax:

```python
def stats(x: Const(Float64[:])) -> tuple[Float64, Float64]: ...
```

For an exact native output argument, keep the native writable argument visible
unless a projection is explicitly supplied:

```python
def get_count(out: Annotated[Ptr(Int32), Intent("out")]) -> None: ...
```

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

Shape expressions can reference earlier arguments or literal bounds:

```python
def resize(n: Int32, values: Float64[1:n]) -> None: ...
def copy3(src: Const(Float64[3]), dst: Float64[3]) -> None: ...
```

For exact C pointer storage that does not carry a proven shape, use `Ptr(T)` or
`Ptr(Const(T))` instead of inventing a NumPy shape:

```python
def dot(n: Int32, x: Ptr(Const(Float64)), y: Ptr(Const(Float64))) -> Float64: ...
```

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

Visibility can be narrowed with `private[...]` or `@private`:

```python
hidden_scale: private[Float64]

@private
def helper(x: Ptr(Const(Int32))) -> None: ...
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

Class fields use the same scalar, array, pointer, and `Annotated[...]` syntax
as function arguments:

```python
class vector3:
    values: Float64[3]

class particle:
    id: Int32
    mass: Float64
    position: Float64[3]
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

Generic constraints also use `Annotated[...]`:

```python
value: Annotated[Int32, Bounded(1, 8), Finite]
alias: Annotated[Float64[:], Name("native_alias")]
```

`Name("...")` changes the native symbol name represented by the semantic
entry; the Python identifier can remain a valid Python spelling.

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

Use the fully specified `Callable[[...], Return]` form when readiness reports a
callback blocker:

```python
from typing import Callable

def integrate(objective: Callable[[Float64], Float64], x0: Float64) -> Float64: ...
```

`Callable[..., Float64]` is accepted syntax, but it intentionally leaves
argument types unknown and may still be too weak for wrapper generation.

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

The supported projection entries today are:

| Entry | Meaning |
| --- | --- |
| `Arg(i)` | Native argument comes from visible Python argument `i`. |
| `Return(i)` | Native argument is represented by Python return value `i`. |
| `Const(value)` | Hidden native argument is a literal value. |
| `Len(Arg(i))` | Hidden native argument is the length of argument `i`. |
| `Len(Return(i))` | Hidden native argument is the length of return value `i`. |
| `Arg(i).shape[d]` | Hidden native argument is dimension `d` of argument `i`. |
| `Work("name")` | Hidden native argument is named temporary workspace. |
| `Work("name").shape[d]` | Hidden native argument is a workspace dimension. |
| `IsPresent(Arg(i))` | Hidden native argument records whether optional argument `i` was supplied. |

The list order is the native argument order. Positions are zero-based.

Hidden literal and derived native arguments:

```python
@native_call([
    Arg(0),
    Const(1),
    Len(Arg(0)),
    Arg(0).shape[0],
    IsPresent(Arg(1)),
    Work("tmp"),
])
def wrapper(
    x: Float64[:],
    b: Vector | None = None
) -> None: ...
```

Projection metadata can also reference return values or workspace dimensions:

```python
@native_call([Len(Return(0)), Work("tmp").shape[1]])
def produce_values() -> Float64[:]: ...
```

Method projections work the same way:

```python
class particle:
    @private
    @native_call([Arg(0)])
    def reset(self: particle) -> Int32: ...
```

The `.pyi` loader and printer preserve this projection metadata. Wrapper
generation that actually hides pointer references, allocates workspace,
translates status returns, or applies coercions is still a later wrapper-stage
policy. Syntax such as `Ptr(Arg(...))`, `As[...]`, status checking, and
ownership helpers belongs to that future projection design; do not write it as
current accepted user syntax unless the implementation has added it.

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

### External Owner Stub

When an imported Fortran derived type or external C opaque struct remains
outside the direct wrapping target, generated `.pyi` output can include an
owner-module dependency stub.

Wrapping only `physics.f90` may produce:

```python
# physics.pyi
from types_mod import particle

def move(p: Ptr(particle)) -> None: ...
```

and a companion owner stub:

```python
# types_mod.pyi
class particle(Opaque):
    pass
```

The direct API keeps the correct import, and the owner stub gives readiness a
concrete semantic type. If the owner module is later part of the wrapping
target, replace the opaque placeholder with the edited concrete class.

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
