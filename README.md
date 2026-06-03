# x2py

Wrapper-oriented parser and semantic-interface tooling for Fortran and C. x2py
extracts native declarations, converts them to language-neutral semantic IR,
emits editable `.pyi` interface files, and reports whether an interface has
enough information for future wrapper generation.

[![Tests](https://github.com/PyNumLab/x2py/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/PyNumLab/x2py/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/PyNumLab/x2py/graph/badge.svg?token=QZRRCS5YO6)](https://codecov.io/gh/PyNumLab/x2py)

## Documentation Levels

Use the README for orientation and common commands. Then use the audience
specific docs when you need detail:

- [User documentation](docs/user.md): more CLI cases, Python API workflows,
  `.pyi` format, datatype mappings, readiness reports, and user policy
  responsibilities.
- [Developer documentation](docs/developer.md): project internals, source
  ownership, parser/semantic contracts, fixture maintenance, and focused test
  commands.
- [C parser reference](docs/c_parser.md) and
  [Fortran parser reference](docs/fortran_parser.md): parser-specific coverage,
  behavior, diagnostics, and maintenance notes.
- [Semantic IR and `.pyi` reference](docs/semantics.md): full semantic contract
  details.

## What x2py Produces

x2py exposes four user-facing stages:

- `--parse`: source-faithful parser facts and parser diagnostics.
- `--semantics`: language-neutral semantic IR.
- `--pyi`: editable Python `.pyi` semantic interface stubs.
- `--wrap-readiness`: a report that says whether the semantic interface is
  complete enough for wrapping.

The important model is:

```text
native source
  -> parser facts
  -> semantic IR
  -> editable .pyi
  -> readiness report
  -> future wrapper generation
```

x2py is not a full compiler frontend. It preserves declarations, signatures,
types, source locations, include/use relationships, diagnostics, and semantic
metadata needed for wrapper generation. It does not silently infer pointer
ownership, callback lifetime, ABI shims, or Pythonic projections; users provide
that policy in `.pyi` when source code alone is not enough.

## Parser Coverage At A Glance

Fortran support focuses on wrapper-relevant source facts:

- free-form and fixed-form source;
- subroutines, functions, modules, submodules, programs, and block data;
- intrinsic scalar types, kind facts, `intent`, `optional`, `value`,
  `allocatable`, `pointer`, and array ranks/shapes;
- derived types, fields, type-bound procedures, and generic bindings;
- module-level variables, `use` dependencies, renamed imports, native
  includes, and cross-file project context;
- source locations, parse diagnostics, and unsupported-construct blockers.

C support focuses on declaration/signature extraction:

- compiler-preprocessed C source and headers in CLI workflows;
- function declarations/definitions, variables, typedefs, structs, unions,
  enums, incomplete tags, arrays, pointers, function pointers, and redeclaration
  merging;
- include/index facts, source-location remapping, compiler-extension warnings,
  standard-type probe facts, and parser diagnostics;
- semantic IR conversion, `.pyi` generation, and readiness for the supported C
  subset.

For C and Fortran source that depends on preprocessing, the CLI uses compiler
preprocessing. C defaults to `cc` and Fortran defaults to `gfortran` unless you
pass `--compiler`, `--compile-commands`, or a custom preprocessing template.

## CLI Quick Start

Parse a Fortran source:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
```

Typical output:

```text
File: tests/data/fortran/general/basic_subroutine.f90
  Modules: 1
    - module m1 (vars=0, uses=0)
      Procedures: 1
        - subroutine add1(n:integer[0], x:real(8)[1])
```

Generate exact native `.pyi` stubs:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
```

```python
File: tests/data/fortran/general/basic_subroutine.f90
def add1(
    n: Ptr(Const(Int32)),
    x: Float64[n]
) -> None: ...
```

Check readiness:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
```

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

Parse C explicitly:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --parse
```

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

Generate C `.pyi` stubs:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --pyi
```

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
```

Use `--json` with any stage that supports structured output:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --parse --json
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness --json
```

Write output to a file or beside each source:

```bash
python -m x2py path/to/file.f90 --parse --json --out report.json
python -m x2py path/to/file.f90 --pyi --out module.pyi
python -m x2py path/to/src_dir --language fortran --parse --out
```

## Language Selection

Recognizable Fortran files and `.pyi` readiness inputs can omit `--language`.
C files, directories, and unknown-suffix inputs must choose the frontend
explicitly:

```bash
python -m x2py path/to/fortran_src --language fortran --parse
python -m x2py path/to/c_src --language c --parse
```

Fortran directories scan `.f`, `.for`, `.ftn`, `.f90`, `.f95`, `.f03`, and
`.f08`. C directories scan `.c`, `.h`, and `.i`.

Fortran-only display helpers:

```bash
python -m x2py path/to/file.f90 --parse --show-vars
python -m x2py path/to/file.f90 --parse --print-limit 50
```

## Compiler Flags And Preprocessing

The CLI preprocessing path is the wrapper-facing path. The selected compiler is
authoritative for macro expansion, conditional branches, includes, predefined
macros, target flags, and sysroot behavior.

Parse C with an exact compiler and API flags:

```bash
python -m x2py path/to/api.h --language c --parse \
  --compiler clang-18 \
  -I include \
  -D API_EXPORT= \
  --std c11
```

Parse C with target/sysroot flags:

```bash
python -m x2py path/to/api.c --language c --parse \
  --compiler /usr/bin/gcc-13 \
  --compiler-arg=--sysroot=/opt/sdk
```

Parse C using `compile_commands.json`:

```bash
python -m x2py path/to/api.c --language c --parse \
  --compile-commands build/compile_commands.json
```

Parse Fortran with a specific compiler and preprocessing flags:

```bash
python -m x2py path/to/file.F90 --language fortran --parse \
  --compiler /usr/bin/gfortran-12 \
  -I include \
  -D USE_MPI \
  --std f2008 \
  --compiler-arg=-fdefault-real-8
```

Use a custom preprocessing command template for unsupported compiler families:

```bash
python -m x2py path/to/api.h --language c --parse \
  --preprocessor-adapter command-template \
  --preprocess-template 'cc -E {include_dirs} {defines} {source}'
```

Control include exposure for generated wrapper-facing interfaces:

```bash
python -m x2py include/api.h --language c --pyi \
  --include-exposure roots-only \
  --public-include 'include/public/*' \
  --private-include 'vendor/*'
```

Target-dependent type facts are not hard-coded. Probe them with the same
compiler and target-relevant flags:

```bash
python -m x2py.c_type_probe --compiler /usr/bin/gcc-13 \
  -I include \
  --std c11 \
  --compiler-arg=--sysroot=/opt/sdk

python -m x2py.fortran_type_probe --compiler /usr/bin/gfortran-12 \
  --expr 'selected_real_kind(12)' \
  --expr 'selected_int_kind(9)' \
  --std f2008 \
  --compiler-arg=-fdefault-real-8
```

## `.pyi` Is The Editable Contract

Generated `.pyi` files preserve exact native contracts by default. They do not
hide native pointer arguments, infer ownership, or turn output arguments into
Python return values unless the `.pyi` explicitly says so.

If source facts are not enough, generate a draft, edit it, and check readiness:

```bash
python -m x2py solver.f90 --pyi --out solver.pyi
python -m x2py solver.pyi --wrap-readiness
```

Opaque handles are represented explicitly:

```python
class context(Opaque):
    pass

def context_create() -> Ptr(context): ...
def context_destroy(ctx: Ptr(context)) -> None: ...
```

When an imported Fortran derived type or external C opaque struct belongs to an
owner module/header outside the direct wrapping target, `.pyi` generation can
emit an owner-module dependency stub:

```python
# physics.pyi
from types_mod import particle

def move(p: Ptr(particle)) -> None: ...
```

```python
# types_mod.pyi
class particle(Opaque):
    pass
```

That means the direct API keeps the correct import, while the owner stub gives
readiness a concrete semantic type to reconcile. Users can later replace the
opaque owner class with a more detailed edited class when the owner module is
part of the wrapping target.

## Python API

Common public entrypoints:

```python
from x2py import (
    parse_fortran_file,
    parse_fortran_project,
    parse_c_file,
    parse_c_project,
    fortran_file_to_semantic_modules,
    c_file_to_semantic_modules,
    emit_module_stubs,
    assess_semantic_wrap_readiness,
    assess_pyi_wrap_readiness,
)
```

Parse one source:

```python
from x2py import parse_fortran_file, parse_c_file

fortran_file = parse_fortran_file("path/to/file.f90")
c_file = parse_c_file("int add(int a, int b);", filename="api.h")
```

Convert to semantic IR and readiness:

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

Direct Python parser entrypoints can be useful for controlled strings, focused
tests, and already-preprocessed inputs. For real wrapper workflows involving
macros, includes, target flags, or compiler-dependent types, prefer the CLI
compiler-preprocessed path or build an equivalent preprocessing configuration.

## Repository Layout

- `fortran_parser/`: Fortran parser frontend.
- `c_parser/`: C parser frontend.
- `semantics/`: semantic IR conversion, `.pyi` loading/printing, datatype
  mapping, and wrap-readiness checks.
- `x2py/`: package entrypoints, preprocessing, and CLI integration.
- `tests/`: parser, semantic, CLI, fixture, and property tests.
- `docs/`: user, developer, parser, semantic, quality, and design references.

## Running Tests

From the repository root:

```bash
PYTHONPATH=. pytest -q
```

Focused commands for parser changes, semantic changes, CLI changes, fixture
regeneration, linting, and coverage are in
[Developer Documentation](docs/developer.md#testing-map).
