# x2py

Wrapper-oriented parser and semantic-interface tooling for Fortran and C. x2py
extracts native declarations, converts them to language-neutral semantic IR,
emits editable `.pyi` interface files, and reports whether an interface has
enough information for future wrapper generation.

[![Tests](https://github.com/PyNumLab/x2py/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/PyNumLab/x2py/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/PyNumLab/x2py/graph/badge.svg?token=QZRRCS5YO6)](https://codecov.io/gh/PyNumLab/x2py)

## Documentation

Use the README for orientation and common commands. Then continue with:

- [Tutorial](docs/tutorial.md): supported end-to-end Fortran and C workflows,
  semantic `.pyi` editing, readiness, and current limitations.
- [Verified examples cookbook](docs/examples.md): more CLI commands, compiler
  preprocessing recipes, Python API examples, and readiness blocker examples.
- [Developer guide](docs/developper_guide.md): project internals, support
  evidence rules, source ownership, fixture maintenance, and focused tests.
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

## Fortran Quick Start

Parse a Fortran source. The command below uses this complete input file:

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

Command:

<!-- x2py-doc-test: exact -->
```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
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

Generate exact native `.pyi` stubs from the same Fortran file:

<!-- x2py-doc-test: exact -->
```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
```

<!-- x2py-doc-test-output -->
```python
File: tests/data/fortran/general/basic_subroutine.f90
def add1(
    n: Ptr(Const(Int32)),
    x: Float64[n]
) -> None: ...
```

Check readiness for the same Fortran file:

<!-- x2py-doc-test: exact -->
```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
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

## C Quick Start

Parse C explicitly. The command below uses this complete input header:

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

Command:

<!-- x2py-doc-test: exact -->
```bash
python -m x2py tests/data/c/general/math_api.h --language c --parse
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

Generate C `.pyi` stubs from the same header:

<!-- x2py-doc-test: exact -->
```bash
python -m x2py tests/data/c/general/math_api.h --language c --pyi
```

<!-- x2py-doc-test-output -->
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

Check C readiness for the same header:

<!-- x2py-doc-test: exact -->
```bash
python -m x2py tests/data/c/general/math_api.h --language c --wrap-readiness
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

Generate C semantic IR:

<!-- x2py-doc-test: run -->
```bash
python -m x2py tests/data/c/general/math_api.h --language c --semantics
```

The semantic output contains `semantic_modules` plus the generated `pyi` text
for the supported C subset.

## Output Modes And Print Size

By default, `--parse` prints a compact human-readable report. For full
machine-readable parser facts, use `--json`:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --parse --json
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness --json
```

Fortran human-readable parse output keeps scope variables summarized as
`vars=N` by default. Use `--show-vars` to expand variables. For both Fortran
and C, use `--print-limit N` to cap repeated sections in the human-readable
parse report:

The Fortran truncation example uses this complete input file:

`tests/data/fortran/general/modern_pyi_example.f90`

```fortran
module modern_math_physics
  implicit none
  private
  public :: particle, vector3, counter, init_particle, kinetic_energy, scale_vector, dot3, fill_identity3, normalize_particle

  integer :: counter
  real(8) :: hidden_scale

  type :: particle
     integer :: id
     real(8) :: mass
     real(8), dimension(3) :: position
  end type particle

  type :: vector3
     real(8), dimension(3) :: values
  end type vector3

  type :: hidden_state
     integer :: code
  end type hidden_state

contains

  subroutine init_particle(p, pid, mass, x, y, z)
    type(particle), intent(out) :: p
    integer, intent(in) :: pid
    real(8), intent(in) :: mass, x, y, z
    p%id = pid
    p%mass = mass
    p%position = [x, y, z]
  end subroutine init_particle

  function kinetic_energy(p, vx, vy, vz) result(e)
    type(particle), intent(in) :: p
    real(8), intent(in) :: vx, vy, vz
    real(8) :: e
    e = 0.5d0 * p%mass * (vx*vx + vy*vy + vz*vz)
  end function kinetic_energy

  subroutine scale_vector(v, alpha)
    real(8), dimension(:), intent(inout) :: v
    real(8), intent(in) :: alpha
    v = alpha * v
  end subroutine scale_vector

  function dot3(a, b) result(s)
    real(8), dimension(3), intent(in) :: a, b
    real(8) :: s
    s = a(1)*b(1) + a(2)*b(2) + a(3)*b(3)
  end function dot3

  subroutine fill_identity3(a)
    real(8), dimension(3,3), intent(out) :: a
    a = 0.0d0
    a(1,1) = 1.0d0
    a(2,2) = 1.0d0
    a(3,3) = 1.0d0
  end subroutine fill_identity3

  subroutine normalize_particle(p)
    type(particle), intent(inout) :: p
    real(8) :: n
    n = sqrt(dot3(p%position, p%position))
    if (n > 0.0d0) p%position = p%position / n
  end subroutine normalize_particle

  subroutine hidden_proc(x)
    integer, intent(in) :: x
  end subroutine hidden_proc

end module modern_math_physics
```

Command:

```bash
python -m x2py tests/data/fortran/general/modern_pyi_example.f90 \
  --parse \
  --show-vars \
  --print-limit 2
```

Example truncated output:

```text
File: tests/data/fortran/general/modern_pyi_example.f90
  Modules: 1
    - module modern_math_physics (vars=2, uses=0)
      Variables: 2
        - counter:integer[0]
        - hidden_scale:real(8)[0]
      Derived types: 3
        - type particle (fields=3, methods=0)
          Fields: 3
            - id:integer[0]
            - mass:real(8)[0]
            ... 1 more fields
        - type vector3 (fields=1, methods=0)
          Fields: 1
            - values:real(8)[1]
        ... 1 more derived types
      Procedures: 7
        - subroutine init_particle(p:type(particle)[0], pid:integer[0], mass:real(8)[0], x:real(8)[0], y:real(8)[0], z:real(8)[0])
        - function kinetic_energy(p:type(particle)[0], vx:real(8)[0], vy:real(8)[0], vz:real(8)[0]) -> real(8)[0]
        ... 5 more procedures
```

For C, `--print-limit` expands the compact counts into a bounded list of
declarations per section. This command uses the `math_api.h` header shown in
the C Quick Start:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --parse --print-limit 2
```

```text
File: tests/data/c/general/math_api.h
  Language: c
  Functions: 4
    - norm2
    - scale
    ... 2 more functions
  Structs: 0
  Unions: 0
  Enums: 0
  Typedefs: 0
  Variables: 0
  Macros: 0
  Includes: 0
  Diagnostics: 0
```

Use `--json` when you need complete function, type, source-location,
preprocessing, and diagnostic facts.

Write output to a file or beside each source with `--out`:

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

Display helpers:

```bash
python -m x2py path/to/file.f90 --parse --show-vars
python -m x2py path/to/file.f90 --parse --print-limit 50
python -m x2py path/to/api.h --language c --parse --print-limit 50
```

`--show-vars` is Fortran-only. `--print-limit` applies to both Fortran and C
human-readable parse reports.

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
- `docs/`: tutorial, examples, developer, parser, semantic, quality, and
  design references.

## Running Tests

From the repository root:

```bash
PYTHONPATH=. pytest -q
```

Focused commands for parser changes, semantic changes, CLI changes, fixture
regeneration, linting, and coverage are in the
[Developer Guide](docs/developper_guide.md#testing-map).
