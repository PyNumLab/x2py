# Tutorial

This tutorial walks through the supported x2py pipeline from native source to
semantic readiness. The commands use version-controlled fixtures so they can be
run from the repository root.

For more task-specific commands and Python snippets, use the
[examples cookbook](examples.md). For the complete semantic `.pyi` contract,
use the [semantic reference](semantics.md).

## Current Scope

x2py currently supports four user-facing stages:

1. Parse wrapper-relevant Fortran or C declarations.
2. Convert parser facts to language-neutral semantic IR.
3. Emit an editable semantic `.pyi` interface.
4. Report whether that semantic interface has enough information for future
   wrapper generation.

x2py does **not** currently generate, compile, or load a runtime wrapper.
`Wrappable: yes` means the semantic contract has no known readiness blockers;
it does not mean a compiled Python extension already exists.

The supported pipeline is:

```text
Fortran or C source
  -> parser facts
  -> semantic IR
  -> editable .pyi
  -> semantic readiness report
```

Parsers preserve source facts. Semantic IR normalizes those facts. Edited
`.pyi` files are the user-controlled contract when source alone cannot express
enough policy. Readiness reports blockers rather than guessing ownership,
callback lifetime, ABI shims, or Python-visible projections.

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

This walkthrough uses:

```text
tests/data/fortran/general/basic_subroutine.f90
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

## C Walkthrough

This walkthrough uses:

```text
tests/data/c/general/math_api.h
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
It is not a C++ frontend or a full compiler frontend. See the
[C parser reference](c_parser.md) for the maintained supported subset.

## Choose A Stage

| Goal | Command flag | Output |
| --- | --- | --- |
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
python3 -m x2py src/api.c --language c --semantics \
  --compile-commands build/compile_commands.json
```

For Fortran:

```bash
python3 -m x2py src/api.f90 --language fortran --pyi \
  --compiler gfortran \
  -I include \
  -D USE_MPI \
  --std f2008 \
  --compiler-arg=-fdefault-real-8
```

Compiler preprocessing preserves a recipe in machine-readable parser output,
including the selected compiler, arguments, includes, source mappings, and
diagnostics. See the [examples cookbook](examples.md#compiler-preprocessing)
for more supported preprocessing modes.

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
preserved, but x2py does not yet execute projections or generate runtime
wrapper code. See the [semantic reference](semantics.md) before writing custom
semantic annotations.

## Use The Python API

The package exports parser, semantic conversion, `.pyi`, and readiness helpers.

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
future wrapper policy or implementation work and cannot currently be resolved
by an annotation.

## Supported Boundaries

Use x2py for the behavior implemented and tested today:

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
- generated or compiled runtime wrappers;
- execution of `@native_call` projections.

The maintained inventories are the
[Fortran parser reference](fortran_parser.md),
[C parser reference](c_parser.md), and
[semantic reference](semantics.md).

## Continue Reading

- [Verified examples cookbook](examples.md)
- [Semantic IR and `.pyi` reference](semantics.md)
- [Diagnostic code registry](diagnostic_codes.md)
- [Fortran parser reference](fortran_parser.md)
- [C parser reference](c_parser.md)
- [Developer guide](developper_guide.md)
