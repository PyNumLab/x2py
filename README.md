# x2py

Wrapper-oriented parser and semantic-interface tooling for Fortran and C. x2py
extracts native declarations, converts them to language-neutral semantic IR,
emits editable `.pyi` interface files, and reports whether an interface has
enough information for future wrapper generation.

[![Quality](https://github.com/PyNumLab/x2py/actions/workflows/quality.yml/badge.svg?branch=main)](https://github.com/PyNumLab/x2py/actions/workflows/quality.yml)
[![codecov](https://codecov.io/gh/PyNumLab/x2py/graph/badge.svg?token=QZRRCS5YO6)](https://codecov.io/gh/PyNumLab/x2py)

## Quick Start

x2py requires Python 3.10 or newer. Install a checkout and inspect the CLI:

```bash
python3 -m pip install -e .
python3 -m x2py --help
```

The default user-facing action for a single Fortran source is to build a Python
extension:

```bash
python3 -m x2py solver.f90
```

The inspection workflow also has four explicit stages:

```text
native source
  -> parser facts
  -> semantic IR
  -> editable .pyi
  -> readiness report
  -> future wrapper generation
```

| Goal | Command flag |
| --- | --- |
| Inspect native declarations and diagnostics | `--parse` |
| Consume language-neutral semantic facts | `--semantics` |
| Generate an editable semantic interface | `--pyi` |
| Find missing information or unsupported contracts | `--wrap-readiness` |

`Wrappable: yes` means the semantic contract has no known readiness blockers.
The current runtime wrapper build path is implemented for single Fortran
sources; C runtime wrapping is still tracked through semantic readiness until
the C wrapper backend is completed.
The [generated target datatype mapping example](docs/semantics.md#generated-linux-x86_64-mapping-example)
shows how the GitHub Actions C and Fortran scalar types map to NumPy dtypes.

### Fortran

Recognizable Fortran files do not require an explicit language. Parse the
checked basic-subroutine fixture:

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

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
```

<!-- x2py-doc-test-output -->
```text
File: tests/data/fortran/general/basic_subroutine.f90
  Modules: 1
    - module m1 (vars=0, uses=0)
      Procedures: 1
        - subroutine add1(n:integer[0], x:real(8)[1])
```

Generate its editable `.pyi` contract:

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
```

<!-- x2py-doc-test-output -->
```python
File: tests/data/fortran/general/basic_subroutine.f90
def add1(
    n: Ptr(Const(Int32)),
    x: Float64[n]
) -> None: ...
```

Check semantic readiness:

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
```

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

Write a draft interface, edit it when source facts are not enough, then check
the edited contract:

```bash
python3 -m x2py solver.f90 --pyi --out solver.pyi
python3 -m x2py solver.pyi --wrap-readiness
```

### C

C inputs require explicit C mode. These commands parse the checked C API
fixture, inspect semantic IR, generate its `.pyi`, and check readiness:

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

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --parse
```

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

<!-- x2py-doc-test: run -->
```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --semantics
```

<!-- x2py-doc-test: run -->
```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --pyi
```

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --wrap-readiness
```

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

## Native Project Inputs

The CLI uses compiler preprocessing for native source. C defaults to `cc` and
Fortran defaults to `gfortran`. Pass the native project's important compiler
and target flags:

```bash
python3 -m x2py include/api.h --language c --parse \
  --compiler clang \
  -I include \
  -D API_EXPORT= \
  --std c11 \
  --compiler-arg=--sysroot=/opt/sdk
```

Compiler-backed semantic, `.pyi`, and readiness stages also measure and cache
target datatype facts. C probing covers primitive ABI widths and signedness;
Fortran probing resolves kind expressions and measures intrinsic storage.

C projects can use a compilation database:

```bash
python3 -m x2py src/api.c --language c --semantics \
  --compile-commands build/compile_commands.json
```

Use `--parse --json` for complete machine-readable parser facts and `--out`
to write selected output to a file or beside each source.

## Python API

Public entrypoints cover parsing, semantic conversion, `.pyi` emission, and
readiness:

```python
from x2py import (
    assess_semantic_wrap_readiness,
    c_file_to_semantic_modules,
    emit_module_stubs,
    parse_c_file,
)

parsed = parse_c_file("int add(int a, int b);", filename="api.h")
modules = c_file_to_semantic_modules(parsed)
stubs = emit_module_stubs(modules)
report = assess_semantic_wrap_readiness(modules, source="api.h")
```

Direct Python parser entrypoints are useful for controlled strings, focused
tests, and already-preprocessed inputs. For native projects with macros,
includes, or target flags, use the compiler-preprocessed CLI path or an
equivalent preprocessing configuration.

## Supported Scope

x2py preserves wrapper-relevant declarations, signatures, types, source
locations, include/use relationships, diagnostics, and semantic metadata.
Current support includes:

- free-form and fixed-form Fortran, procedures, modules, derived types,
  imports, arrays, and wrapper-relevant declaration attributes;
- C declarations and definitions, variables, typedefs, aggregates, enums,
  pointers, arrays, function pointers, includes, and preprocessing facts;
- language-neutral semantic IR, editable `.pyi` interfaces, and semantic
  readiness reports.

x2py is not a full compiler frontend. It does not silently infer pointer
ownership, callback lifetime, ABI shims, or Python-visible projections.

## Documentation

- [Tutorial](docs/tutorial.md): the complete supported user workflow,
  additional recipes, semantic interface editing, readiness, and current
  limitations.
- [Developer guide](docs/developper_guide.md): implementation ownership,
  parser references, testing, fixtures, and change workflows.

## Development

Run the full suite from the repository root:

```bash
PYTHONPATH=. python3 -m pytest -q
```

Focused verification commands and fixture-maintenance workflows are in the
[Developer guide](docs/developper_guide.md#testing-map).
