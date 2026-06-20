# Tutorial

This tutorial is the main user guide for the supported x2py pipeline from
native source to wrapper builds and semantic readiness. The commands use
version-controlled fixtures so they can be run from the repository root.

For additional copy-paste commands and Python snippets, continue to the
[examples cookbook](examples.md). For detailed user-facing contracts, use the
[semantic `.pyi` format](pyi_format.md), [semantic IR reference](semantics.md),
and
[diagnostic code registry](diagnostic_codes.md). Implementation and parser
maintenance material starts in the [developer guide](developper_guide.md).

## Current Scope

x2py builds one Python extension by default when given one or more ordered
Fortran source files:

```bash
python3 -m x2py solver.f90
```

x2py also supports four explicit inspection stages:

1. Parse wrapper-relevant Fortran or C declarations.
2. Convert parser facts to language-neutral semantic IR.
3. Emit an editable semantic `.pyi` interface.
4. Report whether that semantic interface has enough information for wrapper
   generation, while distinguishing readiness from an available runtime
   backend.

The current runtime wrapper build path is implemented for Fortran source
files. `Wrappable: yes` means the semantic contract has no known readiness
blockers; for C and edited `.pyi` contracts it does not mean a compiled Python
extension already exists. Runtime wrapping of user-supplied C libraries will
be added later.

The implemented Fortran build pipeline is:

```text
ordered Fortran sources
  -> compiler preprocessing and target-type probing
  -> parser project facts
  -> semantic IR
  -> codegen AST
  -> generated Fortran bind(C) bridge
  -> generated C/CPython binding and runtime support
  -> compiled and linked Python extension
```

The inspection pipeline is shared by Fortran and C:

```text
Fortran or C source
  -> parser facts
  -> semantic IR
  -> editable .pyi
  -> semantic readiness report
```

Fortran wrapper generation continues from semantic IR into native codegen.
The current C path stops at semantic readiness; the generated C source used by
the Fortran backend is not a wrapper backend for C inputs.

Parsers preserve source facts. Semantic IR normalizes those facts. Edited
`.pyi` files are the user-controlled inspection and readiness contract when
source alone cannot express enough policy. The current Fortran build remains
source-driven and does not consume an edited `.pyi` directly. Readiness reports
blockers rather than guessing ownership, callback lifetime, ABI shims, or
Python-visible projections.

## Before You Start

x2py requires Python 3.10 or newer. For native source input, the shared CLI
runs compiler preprocessing:

- C defaults to `cc`.
- Fortran defaults to `gfortran`.
- Use `--compiler`, `--compile-commands`, or a custom preprocessing template
  when the native project uses different flags or tools.

Install the checkout and inspect the CLI:

```bash
python3 -m pip install -e .
python3 -m x2py --help
```

The examples below use `python3`. Replace it with the Python 3.10+ executable
for your environment when necessary. After installation, the `x2py` console
command is equivalent to `python3 -m x2py`.

## Fortran Walkthrough

Input (`tests/data/fortran/general/basic_subroutine.f90`):

<!-- x2py-doc-source: tests/data/fortran/general/basic_subroutine.f90 -->
```fortran
module m1
contains
subroutine add1(n, x)
  integer, intent(in) :: n
  real(kind=8), intent(inout), dimension(n) :: x
end subroutine add1
end module m1
```

### 1. Parse The Source

Recognizable Fortran files do not require `--language fortran`:

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
```

Expected output:

<!-- x2py-doc-test-output -->
```text
File: tests/data/fortran/general/basic_subroutine.f90
  Modules: 1
    - module m1 (vars=0, uses=0)
      Procedures: 1
        - subroutine add1(n:integer[0], x:real(8)[1])
```

This is a compact source-fact report. It describes the native module and
procedure signature; it does not decide wrapper policy.

### 2. Inspect Semantic IR

Convert the parsed source to language-neutral semantic IR:

<!-- x2py-doc-test: run -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --semantics
```

`--semantics` prints a machine-readable payload containing `semantic_modules`
and generated `pyi` text. Use it when another tool needs structured semantic
data.

### 3. Generate The Editable Interface

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
```

Expected output:

<!-- x2py-doc-test-output -->
```python
File: tests/data/fortran/general/basic_subroutine.f90
def add1(
    n: Ptr(Const(Int32)),
    x: Float64[n]
) -> None: ...
```

The stub preserves the exact native contract:

- `n` is a read-only scalar reference because the Fortran dummy argument is
  not declared with `value`.
- `x` is a writable rank-one array whose extent is `n`.

Write the stub to an explicit path:

```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 \
  --pyi --out basic_subroutine.pyi
```

Use `--pyi --out` without a path to write a `.pyi` beside each input source.

### 4. Check Semantic Readiness

Check readiness directly from source:

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
```

Expected output:

<!-- x2py-doc-test-output -->
```text
File: tests/data/fortran/general/basic_subroutine.f90
  Source: fortran
  Semantic modules: m1
  Wrappable: yes
  Public functions: 1
  Public classes: 0
  Public variables: 0
  No semantic readiness blockers detected.
```

After editing a generated interface, check the `.pyi` instead:

```bash
python3 -m x2py basic_subroutine.pyi --wrap-readiness
```

Readiness treats the edited `.pyi` contract as the source of truth.

### 5. Build A Fortran Extension

Use the checked runtime example for a complete build and call:

<!-- x2py-doc-source: tests/wrapper/fruntime_abi_f90.f90 -->
```fortran
module fruntime_abi_f90
contains
  real(8) function scale(value, factor) result(output)
    real(8), intent(in) :: value
    real(8), intent(in) :: factor
    output = value * factor
  end function scale
end module fruntime_abi_f90
```

Build it into an explicit directory:

```bash
python3 -m x2py tests/wrapper/fruntime_abi_f90.f90 \
  --wrap \
  --out-dir build/fruntime_abi \
  --json
```

`--wrap` is optional when all inputs have recognizable Fortran suffixes and no
inspection stage is selected. It is shown here to make the build action
explicit. The JSON payload reports the extension name, shared-library path,
generated wrapper sources, and all build artifacts.

Import and call the module:

```python
import sys

import numpy as np

sys.path.insert(0, "build/fruntime_abi")
import fruntime_abi_f90

value = fruntime_abi_f90.scale(np.float64(3.0), np.float64(2.5))
assert value == np.float64(7.5)
```

The exact NumPy scalar types are intentional. The wrapper validates the native
ABI contract instead of silently converting arbitrary Python numeric objects.

Without `--out-dir`, intermediate files go into `__x2py__` beside the first
source and the extension is placed beside that source. Use `--verbose` to print
the executed compiler and linker commands.

### 6. Understand The Generated Boundary

The build lowers semantic IR through two native layers:

1. A generated Fortran `bind(C)` bridge adapts Fortran calling conventions,
   arrays, derived types, optional values, and results to a C-compatible ABI.
2. A generated C/CPython binding validates Python objects, manages ownership
   and references, invokes the bridge, and creates Python or NumPy results.

The x2py runtime support is compiled with those generated sources. The final
link combines user objects, the Fortran bridge, the CPython binding, and the
runtime into one extension module. Generated sources are build artifacts; the
public behavior is the documented semantic and wrapper contract.

For a build-system-controlled workflow, generate sources and a GNU Make build
without compiling:

```bash
python3 -m x2py tests/wrapper/fruntime_abi_f90.f90 \
  --makefile \
  --out-dir build/fruntime_abi \
  --json
```

Then run `make -f build/fruntime_abi/Makefile.x2py`. The Makefile exposes
`FC`, `CC`, `X2PY_LD`, `X2PY_FFLAGS`, `X2PY_CFLAGS`, and `X2PY_LDFLAGS`.
The [Fortran wrapper guide](fortran_wrapper.md) defines the complete Python API
and the [examples cookbook](examples.md#fortran-runtime-wrapper-examples)
contains multi-source and Python API recipes.

## C Walkthrough

Input (`tests/data/c/general/math_api.h`):

<!-- x2py-doc-source: tests/data/c/general/math_api.h -->
```c
#ifndef X2PY_GENERAL_MATH_API_H
#define X2PY_GENERAL_MATH_API_H

double norm2(int n, const double x[static 1]);
void scale(int n, double alpha, double x[static 1]);
double dot(int n, const double *restrict x, const double *restrict y);
void fill_identity3(double a[static 3][3]);

#endif
```

C inputs require explicit C mode:

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --parse
```

Expected output:

<!-- x2py-doc-test-output -->
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

Generate the semantic `.pyi`:

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --pyi
```

Expected output:

<!-- x2py-doc-test-output -->
```python
File: tests/data/c/general/math_api.h
def norm2(
    n: Int,
    x: Const(Float64[1])
) -> Float64: ...

def scale(
    n: Int,
    alpha: Float64,
    x: Float64[1]
) -> None: ...

def dot(
    n: Int,
    x: Ptr(Const(Float64)),
    y: Ptr(Const(Float64))
) -> Float64: ...

def fill_identity3(
    a: Float64[3, 3]
) -> None: ...
```

Check readiness:

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/c/general/math_api.h \
  --language c --wrap-readiness
```

Expected output:

<!-- x2py-doc-test-output -->
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

The C frontend supports wrapper-oriented declaration and signature extraction.
It does not yet lower user C inputs into a compiled extension. That backend
will be added later after its ABI, ownership, and runtime contracts are proved.
The C frontend is not a C++ frontend or a full compiler frontend. The
[supported boundaries](#supported-boundaries) below summarize the user-facing
scope.

## Choose A Stage

| Goal | Command flag | Output |
| --- | --- | --- |
| Build a Fortran extension | no stage flag or `--wrap` | Generated sources, objects, and importable extension |
| Generate an editable native build | `--makefile` | Generated sources and `Makefile.x2py`, without compilation |
| Inspect native parser facts | `--parse` | Human-readable report |
| Consume full parser facts | `--parse --json` | Parser payload |
| Consume language-neutral facts | `--semantics` | Semantic payload |
| Create or inspect the editable contract | `--pyi` | Semantic `.pyi` text |
| Find missing semantic policy | `--wrap-readiness` | Readiness report |
| Script readiness decisions | `--wrap-readiness --json` | Readiness payload |

Multiple stages can be useful together:

```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 \
  --parse --wrap-readiness

python3 -m x2py tests/data/c/general/math_api.h \
  --language c --pyi --wrap-readiness
```

Build mode is separate from inspection mode: `--wrap` and `--makefile` cannot
be combined with `--parse`, `--semantics`, `--pyi`, or `--wrap-readiness`.
Both build modes currently require Fortran source files rather than directories
or `.pyi` inputs.

## Select Inputs And Language

Language selection follows these supported rules:

- Recognizable Fortran files can omit `--language`.
- `.pyi` readiness input can omit `--language`.
- C files require `--language c`.
- Directories and unknown-suffix source files require an explicit language.
- Explicit language selection must agree with recognizable source suffixes.

Parse a directory recursively:

```bash
python3 -m x2py path/to/fortran_sources --language fortran --parse
python3 -m x2py path/to/c_sources --language c --parse
```

Parse multiple explicit inputs:

```bash
python3 -m x2py src/types.f90 src/api.f90 --language fortran --parse
python3 -m x2py include/types.h include/api.h --language c --parse
```

For the direct Python parser APIs, paths, source strings, project mappings,
path sequences, and directories are supported. Those direct APIs parse raw or
already-controlled input; they do not run the shared CLI compiler
preprocessing pipeline.

## Use Native Project Compiler Flags

The CLI preprocesses native source before parsing it. Pass the same important
flags used by the native build:

```bash
python3 -m x2py include/api.h --language c --parse \
  --compiler clang \
  -I include \
  -D API_EXPORT= \
  --std c11 \
  --compiler-arg=--sysroot=/opt/sdk
```

Use a C compilation database when one is available:

```bash
python3 -m x2py.c_type_probe --compiler clang \
  --compiler-arg=--target=aarch64-linux-gnu \
  --runner=qemu-aarch64 \
  > build/aarch64-c-types.json

python3 -m x2py src/api.c --language c --semantics \
  --compile-commands build/compile_commands.json \
  --c-type-report build/aarch64-c-types.json
```

For normal direct-compiler C semantic, `.pyi`, and readiness stages, x2py
automatically probes primitive widths and plain `char` signedness using the
selected compiler and target flags. It caches the result by compiler identity
and target configuration, so repeated runs do not recompile the probe. Use
`--refresh-c-type-probe` when a sysroot changes in place. For cross compilers,
repeat `--c-type-probe-runner=...` for the runner command and arguments.

NumPy types are used as the Python-side dtype mapping, not as the ABI probe:
NumPy describes the interpreter host and can disagree with a cross compiler or
selected sysroot. Compilation databases and custom preprocessing templates
need an explicit reusable `--c-type-report` because they can contain multiple
target recipes.

For Fortran:

```bash
python3 -m x2py src/api.f90 --language fortran --pyi \
  --compiler gfortran \
  -I include \
  -D USE_MPI \
  --std f2008 \
  --compiler-arg=-fdefault-real-8
```

For direct-compiler Fortran semantic, `.pyi`, and readiness stages, x2py
resolves compiler-dependent kind expressions and measures the storage of every
intrinsic type used by the source. This matters for processor-dependent
numeric kinds and flags such as `-fdefault-real-8` or
`-fdefault-integer-8`. Expression and storage probes are cached by compiler
identity and target configuration. Use `--refresh-fortran-type-probe` after a
sysroot or compiler installation changes in place, and repeat
`--fortran-type-probe-runner=...` for a cross-target runner.

Compilation databases and custom preprocessing templates need an explicit
reusable `--fortran-type-report`, for the same reason as C: one project recipe
can describe multiple target profiles.

Compiler preprocessing preserves a recipe in machine-readable parser output,
including the selected compiler, arguments, includes, source mappings, and
diagnostics. See the [examples cookbook](examples.md#compiler-preprocessing)
for more supported preprocessing modes.

## Inspect Target Datatype Mappings

Generate the native-to-semantic-to-NumPy scalar mapping for the selected
compiler target:

```bash
python3 -m x2py.type_mapping_report --language c
python3 -m x2py.type_mapping_report --language fortran
```

Pass `--compiler` and repeated `--compiler-arg` options to inspect a different
compiler target or target-changing flags. Both mapping commands use persistent
probe caches; `--cache-dir`, `--refresh`, and repeated `--runner` options
control reuse and cross-target execution. The generated
[Linux x86_64 C and Fortran examples](semantics.md#generated-linux-x86_64-mapping-example)
show the complete input facts and resulting NumPy dtype names used by the
GitHub Actions profile. The Fortran table includes modern kinds and legacy
spellings. It also shows the important distinction between fixed-width
`complex*8` and compiler-kind `complex(kind=8)`, and identifies
`character*N` as length syntax.

## Edit A Semantic `.pyi`

Generated `.pyi` files describe exact native contracts by default. They do not
silently hide native arguments, infer ownership, or turn output arguments into
Python return values.

The loader accepts semantic interface syntax such as:

```python
from typing import Callable, Final

nmax: Final[Int32] = 32

class state:
    count: Int32
    values: Float64[nmax]

def integrate(
    objective: Callable[[Float64], Float64],
    x0: Float64
) -> Float64: ...
```

A complete `Callable[[...], Return]` can resolve a callback-signature
readiness blocker. A placeholder such as `Procedure` or
`Callable[..., Return]` remains incomplete because argument types are unknown.

Supported projection metadata such as `@native_call(...)` is parsed and
preserved. The source-driven Fortran wrapper executes the built-in projection
rules documented in the [Fortran wrapper guide](fortran_wrapper.md), but the
CLI does not currently build directly from an edited `.pyi` or execute an
arbitrary edited `@native_call` contract. See the
[semantic `.pyi` format](pyi_format.md) before writing custom annotations.

## Use The Python API

The package exports `build_fortran_extension` as well as parser, semantic
conversion, `.pyi`, and readiness helpers. The
[examples cookbook](examples.md#build-and-import-through-the-python-api) shows
a complete temporary-directory build and import.

Parse inline source:

<!-- x2py-doc-test: run -->
```python
from x2py import parse_c_file, parse_fortran_file

c_file = parse_c_file("int add(int a, int b);", filename="inline.h")
fortran_file = parse_fortran_file(
    "subroutine ping()\nend subroutine ping\n",
    filename="inline.f90",
)

print([function.name for function in c_file.functions])
print([procedure.name for procedure in fortran_file.procedures])
```

Parse a project from an in-memory mapping:

<!-- x2py-doc-test: run -->
```python
from x2py import parse_c_project

project = parse_c_project(
    {
        "types.h": "typedef int api_int;",
        "api.h": '#include "types.h"\napi_int answer(void);',
    }
)

print(sorted(project.files))
print(sorted(project.functions))
```

Convert, emit a stub, and check readiness:

<!-- x2py-doc-test: run -->
```python
from x2py import (
    assess_semantic_wrap_readiness,
    c_file_to_semantic_modules,
    emit_module_stubs,
    parse_c_file,
)

parsed = parse_c_file("int add(int a, int b);", filename="inline.h")
modules = c_file_to_semantic_modules(parsed)
stubs = emit_module_stubs(modules)
report = assess_semantic_wrap_readiness(modules, source="inline.h")

print(stubs["inline"])
print(report["wrappable"])
```

The [examples cookbook](examples.md#python-api-examples) contains additional
verified Python API workflows.

## Understand Readiness

Readiness is a semantic check. It can report blockers such as:

- unresolved semantic types;
- unresolved array-shape symbols or missing compile-time constants;
- incomplete callback signatures;
- ambiguous C pointer ownership;
- C variadic or unspecified-parameter functions;
- unsupported union, bitfield, atomic, volatile, or ABI-sensitive contracts;
- an empty public API.

When the missing information is expressible in supported semantic `.pyi`
syntax, edit the generated interface and rerun readiness. Some blockers require
additional wrapper policy or backend implementation and cannot currently be
resolved by an annotation.

## Supported Boundaries

Use x2py for the behavior implemented and tested today:

- generated and compiled CPython extensions from one or more ordered Fortran
  source files;
- generated Fortran `bind(C)` bridges, C/CPython bindings, and runtime support
  for the contracts in the [Fortran wrapper guide](fortran_wrapper.md);
- wrapper-relevant Fortran and C source-fact extraction;
- compiler-preprocessed CLI workflows;
- typed parser models and language-neutral semantic IR;
- semantic `.pyi` emission and loading;
- semantic readiness reporting.

Do not assume current support for:

- C++ parsing;
- full compiler-grade parsing or ABI validation;
- automatic pointer ownership or lifetime inference;
- automatic callback lifetime/threading policy;
- generated or compiled runtime wrappers from user-supplied C inputs;
- direct CLI wrapper builds from edited `.pyi` files;
- arbitrary edited `@native_call` projection execution through the CLI build.

The [semantic `.pyi` format](pyi_format.md) is the maintained user-facing
contract for editable stubs. The [semantic IR reference](semantics.md) owns
datatype mapping and IR details.
Implementation inventories and parser-maintenance references are linked from
the [developer guide](developper_guide.md#references).

## Continue Reading

- [Verified examples cookbook](examples.md)
- [Fortran wrapper guide](fortran_wrapper.md)
- [Semantic `.pyi` format](pyi_format.md)
- [Semantic IR reference](semantics.md)
- [Diagnostic code registry](diagnostic_codes.md)
- [Developer guide](developper_guide.md): implementation, parser references,
  tests, and maintenance workflows
