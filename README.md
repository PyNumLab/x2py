# x2py

Wrapper-oriented parser and semantic-interface tooling for Fortran, with a
partial C parser frontend that is source-faithful and ready for later semantic
conversion work.

[![Tests](https://github.com/PyNumLab/x2py/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/PyNumLab/x2py/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/PyNumLab/x2py/graph/badge.svg?token=QZRRCS5YO6)](https://codecov.io/gh/PyNumLab/x2py)


## What the parsers handle

The parsers are intentionally robust subset parsers, not full compiler
frontends. They preserve source facts needed for wrapper generation and defer
ABI, ownership, and wrappability policy to semantic stages.

### Fortran parser

Current handled coverage:

- **Source forms**
  - Free-form: `.f90`, `.f95`, `.f03`, `.f08`
  - Fixed-form: `.f`, `.for`, `.ftn` (including classic continuation)
  - Comment stripping and continuation folding
- **Procedures**
  - `subroutine` and `function`
  - Header attributes: `pure`, `elemental`, `recursive`
  - Function `result(...)` handling
- **Arguments and declarations**
  - Intrinsic types: `integer`, `real`, `complex`, `logical`, `character`
  - `kind=...` extraction
  - `intent(in|out|inout)`
  - `optional`, `value`, `allocatable`, `pointer`
  - `dimension(...)` and variable-level shapes like `x(:)` / `x(n)`
- **Modules and project context**
  - Module discovery
  - Module-level variables and `use` dependencies
  - `use ... only:` symbol mappings preserve both imported source names and
    local target names for renamed imports
  - Propagation of module-level `use` into contained procedures
  - Cross-file kind resolution when parsing a namespace/project
  - Submodules, programs, and block data units
- **Derived types**
  - `type :: ... end type`
  - Attributes (e.g. `abstract`) and `extends(...)`
  - Field extraction (intrinsic + `type(...)`)
  - Type-bound procedures and generic bindings
- **Parser diagnostics and metadata**
  - Source locations for parser errors
  - Unknown argument declaration reporting
  - Parse-stage unsupported construct reporting

### C parser

The C frontend is currently parse-only. It supports:

- Raw-source directive metadata for includes and pragmas. Raw macro and
  conditional directives fail with `CPARSE_PREPROCESSING_REQUIRED`; use
  compiler mode so the configured toolchain expands them first.
- Compiler-assisted preprocessing through the shared CLI flags, with `#line`
  and GCC/Clang linemarker remapping back to original source locations.
- Top-level variables, typedefs, function declarations/definitions, structs,
  unions, enums, incomplete tags, flexible array member diagnostics, and
  compatible top-level redeclaration merging.
- Pointer, array, function, and parenthesized declarator shapes, including
  function pointer typedefs/parameters and parameter adjustment metadata.
- Project include/index facts through `parse_c_project(...)`, with includes
  recorded non-recursively: only explicitly supplied files or files below an
  explicitly supplied directory are parsed.
- Compiler mode is the wrapper-facing path for macro-dependent APIs: parse
  each compiler-expanded translation unit separately for each build
  configuration.

The supported C subset continues through semantic IR conversion, `.pyi`
generation, and wrap-readiness.

## Public APIs

Public API entrypoints include:

- `x2py.parse_fortran_file(source_or_path, filename=None, encoding="utf-8") -> FortranFile`
- `x2py.parse_fortran_project(files, encoding="utf-8") -> FortranProject`
- `x2py.parse_c_file(source_or_path, filename=None, include_dirs=None, preprocessing="raw", encoding="utf-8") -> CFile`
- `x2py.parse_c_project(files, include_dirs=None, preprocessing="raw", encoding="utf-8") -> CProject`
- `x2py.fortran_file_to_semantic_modules(parsed_file, standalone_module_name=None) -> list[SemanticModule]`
- `x2py.fortran_project_to_semantic_modules(project) -> list[SemanticModule]`
- `x2py.c_file_to_semantic_modules(parsed_file) -> list[SemanticModule]`
- `x2py.c_project_to_semantic_modules(project) -> list[SemanticModule]`
- `x2py.emit_module_stubs(module_or_modules) -> dict[str, str]`
- `x2py.load_pyi_modules(path_or_paths, encoding="utf-8") -> list[SemanticModule]`
- `x2py.assess_semantic_wrap_readiness(semantic_ir, source=None) -> dict`
- `x2py.assess_pyi_wrap_readiness(path_or_paths, encoding="utf-8") -> dict`
- `x2py.c_type_probe.probe_c_standard_types(config, runner=None) -> CStandardTypeProbeReport`
- `x2py.evaluate_fortran_type_requirements(config, requirements, runner=None) -> dict[str, int]`

## Repository layout

Fortran source inputs live under `tests/data/fortran`. C parser fixtures live
under `tests/data/c` and C parser tests live under `tests/parser/c`.
Stage-specific tests and expected fixtures live under `tests/parser`,
`tests/semantics`, and `tests/pyi`.

Technical documentation is indexed in [`docs/README.md`](docs/README.md). The
editable wrapper `.pyi` format is documented in
[`docs/semantics/pyi_format.md`](docs/semantics/pyi_format.md).

## Terminal usage

`x2py` exposes four stage flags:

- `--parse` for parser output and parse-stage diagnostics
- `--semantics` for semantic IR JSON
- `--pyi` for generated Python stub text
- `--wrap-readiness` for semantic wrap-readiness from either Fortran or `.pyi`

Recognizable Fortran source files and `.pyi` readiness inputs use the Fortran
path when `--language` is omitted. C source/header files require explicit
`--language c`; directories and unknown-suffix source inputs require either
`--language fortran` or `--language c`. C parsing, semantic IR, `.pyi`
generation, and wrap-readiness are available in explicit C mode. Selecting a
frontend that conflicts with a recognized C or Fortran source suffix is an
error. Once selected, a frontend validates the grammar regions it models and
rejects unparsed syntax outside intentionally ignored execution/function
bodies, rather than guessing another language from keyword spellings or
silently dropping malformed input.

Parse failures print a compiler-style diagnostic without a Python traceback.
Use `--debug` to re-raise the parser error and print the traceback;
`--debug-traceback` remains accepted as a compatibility alias. Diagnostic codes
such as `PARSE_UNSUPPORTED_DECLARATION`, `CPARSE_INVALID_SPECIFIER_SEQUENCE`,
and `CPARSE_INVALID_SYNTAX` are stable, explicit error-category identifiers for
tests, tools, and documentation. The current categories are listed in
[`docs/diagnostic_codes.md`](docs/diagnostic_codes.md).

For parse output, `--show-vars` expands scope-level variables that are normally
summarized as `vars=N`. Use `--print-limit N` to keep large repeated sections
readable.

### Run from source tree

```bash
python -m x2py path/to/file.f90 --parse
```

### Run after installation

```bash
x2py path/to/file.f90 --parse
```

One or more recognized Fortran files can omit `--language`. Directory input
must select a frontend explicitly:

```bash
python -m x2py path/to/fortran_src --language fortran --parse
python -m x2py path/to/c_src --language c --parse
```

Fortran directories scan `.f`, `.for`, `.ftn`, `.f90`, `.f95`, `.f03`,
`.f08`; C directories scan `.c`, `.h`, and `.i` files.

### Compiler preprocessing, includes, and target probes

Wrapper-facing CLI source parsing uses compiler preprocessing. The selected
compiler is authoritative for
macro expansion, `#if`/`#ifdef` branch selection, C `#include`, Fortran CPP
`#include`, predefined macros, `-D`/`-U`, include paths, target flags, and
sysroot behavior. If no compiler is specified, C defaults to `cc` and Fortran
defaults to `gfortran`. Compiler linemarkers remain accepted for provenance.

The shared compiler mode is:

```bash
python -m x2py path/to/source.f90 --language fortran --parse \
  --compiler /path/to/compiler \
  -I include \
  -D FEATURE=1 \
  -U DEBUG \
  --std f2008 \
  --compiler-arg=-fdefault-real-8
```

For C, `--language c` runs the compiler preprocessor and parses stdout. C and
Fortran can use `--compile-commands build/compile_commands.json` when a
matching entry supplies the compiler and project flags. GCC-compatible C/Clang
invocations use `-E -x c`; GNU Fortran invocations use `-E -cpp`. Linemarkers
are preserved so parser locations can be
mapped back to original files. For unsupported compiler families, use
`--preprocessor-adapter command-template --preprocess-template '...'`; the
minimum adapter contract is expanded source on stdout.

Fortran native `include "file.inc"` is resolved after compiler CPP output and
before parsing. This is textual insertion into the current module, procedure,
interface, or execution scope; it is not the same as `use module_name`. Native
includes are resolved relative to the including file first, then configured
`-I` directories, and duplicate textual inclusion is preserved. Missing
includes and cycles are reported as preprocessing diagnostics.

Preprocessing JSON records the exact recipe: compiler or adapter, argv, working
directory, include directories, defines, undefs, standard, extra compiler
arguments, included files, source mappings, diagnostics, and optional macro
metadata when the adapter output exposes it. System-header declarations are
classified private by default. Reachable project includes are public by
default; use `--include-exposure roots-only`, `--public-include`, and
`--private-include` to control wrapper export. Private declarations remain
available internally for type resolution. Public signatures that refer to
private C handle types can use private opaque classes rather than exposing data
members.

The C parser tolerates common compiler-expanded declaration syntax from system
headers, including GNU attributes, `__declspec(...)`, alternate qualifier
spellings, declaration-level `asm(...)`, calling-convention keywords,
`typeof(...)`, `_BitInt(...)`, and selected extended scalar names. Harmless
syntax is accepted without exposing private header declarations. Ignored
extensions that can affect ABI, layout, symbol identity, or type identity
produce `C_UNMODELED_COMPILER_EXTENSION` warnings.

Preprocessing failures print explicit categories such as
`PREPROCESSOR_NOT_FOUND`, `PREPROCESSOR_FAILED`,
`INVALID_COMPILER_ARGUMENTS`, `UNSUPPORTED_COMPILER_CAPABILITY`,
`PROVENANCE_UNAVAILABLE`, `INCLUDE_NOT_FOUND`, and `INCLUDE_CYCLE` without a
Python traceback. Pass `--debug` to re-raise and show the traceback.

Target-dependent type facts are not hard-coded. They are probed with the same
compiler path and target-relevant flags because results may change with ABI,
architecture, library headers, and compiler options.

C standard-header facts:

```bash
python -m x2py.c_type_probe --compiler /usr/bin/gcc-13 \
  -I include \
  -D FEATURE=1 \
  -U DEBUG \
  --std c11 \
  --compiler-arg=--sysroot=/opt/sdk
```

The C probe passes `-I`, `-D`, `-U`, and `--compiler-arg` into the generated
probe and records the requested `--std`. The generated probe itself is compiled
as C11 because it uses C11 `_Generic` and `_Alignof`; if a standard-selection
flag affects the target ABI or headers, pass a compatible override through
`--compiler-arg`. The probe does not consume `compile_commands.json` directly;
when the parser uses a compile database, pass the selected compiler and
target-relevant flags from that entry to the probe explicitly.

Fortran kind/compile-time facts:

```bash
python -m x2py.fortran_type_probe --compiler /usr/bin/gfortran-12 \
  --expr 'selected_real_kind(12)' \
  --expr 'selected_int_kind(9)' \
  --std f2008 \
  --compiler-arg=-fdefault-real-8
```

The Fortran probe passes `-I`, `-D`, `-U`, `--std`, and `--compiler-arg` to the
generated probe. The semantic CLI path uses this automatically when Fortran
input is converted with compiler preprocessing: it collects
unresolved compiler-dependent values, evaluates them with the probe, and feeds
the resulting `compile_time_values` into semantic conversion.

By default the probes execute the generated binary on the host. For cross
targets, provide a compatible runner/emulator or supply a target profile; host
execution only describes the host target.

### C parser examples

Parse a C header:

```bash
python -m x2py include/api.h --language c --parse
```

Print C parser JSON:

```bash
python -m x2py include/api.h --language c --parse --json
```

Parse a macro-shaped API through the configured compiler preprocessor:

```bash
python -m x2py include/api.h --language c --parse \
  --compiler clang-18 \
  -I include \
  -D API_EXPORT=
```

Parse a C source using a compile database entry:

```bash
python -m x2py src/api.c --language c --parse \
  --compile-commands build/compile_commands.json
```

The supported C subset now continues through semantic IR, `.pyi` output, and
wrap-readiness:

```bash
python -m x2py include/api.h --language c --semantics
python -m x2py include/api.h --language c --pyi
python -m x2py include/api.h --language c --wrap-readiness
```

### Example 1: human-readable output

Fortran input (`tests/data/fortran/general/basic_subroutine.f90`):

```fortran
module m1
  implicit none
  integer :: n
  real, dimension(10) :: x
contains
  subroutine add1(n, x)
    integer, intent(in) :: n
    real, dimension(n), intent(inout) :: x
  end subroutine add1
end module m1
```

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
```

Expected style of output:

```text
File: tests/data/fortran/general/basic_subroutine.f90
  Modules: 1
    - module m1 (vars=2, uses=0)
      Procedures: 1
        - subroutine add1(n:integer[0], x:real[1])
```

To include module variables in the same tree:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse --show-vars
```

```text
File: tests/data/fortran/general/basic_subroutine.f90
  Modules: 1
    - module m1 (vars=2, uses=0)
      Variables: 2
        - n:integer[0]
        - x:real[1]
      Procedures: 1
        - subroutine add1(n:integer[0], x:real[1])
```

For large modules, cap repeated sections:

```bash
python -m x2py path/to/file.f90 --parse --show-vars --print-limit 50
```

`--print-limit` applies independently to each repeated section in the
human-readable parse tree, including modules, submodules, programs, block data
units, derived types, fields, procedures, and variables when `--show-vars` is
also set. Section totals are still printed before truncation.

### Example 1b: more complex tree output

Fortran input (`mixed_example.f90`):

```fortran
subroutine driver(n)
  integer, intent(in) :: n
end subroutine driver

module math_ops
  use iso_c_binding, only: c_double
  implicit none
  real(c_double) :: alpha
contains
  subroutine saxpy(n, a, x, y)
    integer, intent(in) :: n
    real(c_double), intent(in) :: a
    real(c_double), dimension(n), intent(in) :: x
    real(c_double), dimension(n), intent(inout) :: y
  end subroutine saxpy

  function dot(x, y) result(r)
    real(c_double), dimension(:), intent(in) :: x, y
    real(c_double) :: r
  end function dot
end module math_ops

module io_ops
  implicit none
contains
  subroutine dump(v)
    real, dimension(:), intent(in) :: v
  end subroutine dump
end module io_ops
```

Command:

```bash
python -m x2py mixed_example.f90 --parse
```

Expected output style:

```text
File: mixed_example.f90
  Procedures: 1
    - subroutine driver(n:integer[0])
  Modules: 2
    - module math_ops (vars=1, uses=1)
      Procedures: 2
        - subroutine saxpy(n:integer[0], a:real[0], x:real[1], y:real[1])
        - function dot(x:real[1], y:real[1])
    - module io_ops (vars=0, uses=0)
      Procedures: 1
        - subroutine dump(v:real[1])
```

Notes:

- Top-level `Procedures` contains only free procedures (not inside a module).
- Module members are listed under each `module ...` entry.
- Empty sections are omitted.

### Example 2: JSON output to stdout

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse --json
```

Expected JSON structure (top-level keyed by input path):

- `<file>.signatures`: parsed procedures
- `<file>.types`: parsed derived types
- `<file>.modules`: parsed modules
- `<file>.submodules`: parsed submodules
- `<file>.programs`: parsed programs
- `<file>.block_data`: parsed block data units

### Example 3: wrap-readiness summary

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
```

This converts each input to semantic IR, then prints the wrappability status
and blocker list. The same flag accepts edited `.pyi` files:

```bash
python -m x2py solver.pyi --wrap-readiness
```

Use `--json` for the stable readiness payload. It keeps `wrappable` at file
level and includes `unit_blockers` only for units that own a blocker.

`--wrap-readiness` can also be combined with other stages. For example,
`--semantics --wrap-readiness` emits semantic IR with a `wrap_readiness` payload
attached, and `--parse --wrap-readiness` prints the parse tree followed by the
semantic readiness summary. Parser JSON remains parse-only; when `--json` is
used with `--parse --wrap-readiness`, the output is split into top-level
`parse` and `wrap_readiness` sections.

### Example 4: semantic IR JSON output

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --semantics
```

This prints semantic conversion payload per file, including:

- `semantic_modules`: semantic module/class/function/type metadata
- `pyi`: generated `.pyi` text associated with those semantic modules

### Example 5: print generated `.pyi` text

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
```

This prints a per-file section followed by the generated Python stub text.


### Example 6: modern Fortran module -> `.pyi` (reproducible fixture)

The repository includes a richer modern-Fortran fixture at:

- `tests/data/fortran/general/modern_pyi_example.f90`

Generate its stubs:

```bash
python -m x2py tests/data/fortran/general/modern_pyi_example.f90 --pyi
```

Current `.pyi` output for this fixture (showing derived types, array annotations, and procedures):

```python
File: tests/data/fortran/general/modern_pyi_example.f90
class particle:
    id: Int32
    mass: Float64
    position: Float64[3]

class vector3:
    values: Float64[3]

@private
class hidden_state:
    code: Int32

counter: Int32

hidden_scale: private[Float64]

def init_particle(
    p: Annotated[Ptr(particle), Intent('out')],
    pid: Ptr(Const(Int32)),
    mass: Ptr(Const(Float64)),
    x: Ptr(Const(Float64)),
    y: Ptr(Const(Float64)),
    z: Ptr(Const(Float64))
) -> None: ...

def kinetic_energy(
    p: Ptr(Const(particle)),
    vx: Ptr(Const(Float64)),
    vy: Ptr(Const(Float64)),
    vz: Ptr(Const(Float64))
) -> Float64: ...

def scale_vector(
    v: Float64[::Strided],
    alpha: Ptr(Const(Float64))
) -> None: ...

def dot3(
    a: Const(Float64[3]),
    b: Const(Float64[3])
) -> Float64: ...

def fill_identity3(
    a: Annotated[Float64[3, 3], ORDER_F, Intent('out')]
) -> None: ...

def normalize_particle(
    p: Ptr(particle)
) -> None: ...

@private
def hidden_proc(
    x: Ptr(Const(Int32))
) -> None: ...
```

This snapshot is also verified in `tests/semantics/test_pyi_printer_modern_example.py`.

Parse output for the same fixture now includes the derived type definition and field list:

```bash
python -m x2py tests/data/fortran/general/modern_pyi_example.f90 --parse
```

```text
File: tests/data/fortran/general/modern_pyi_example.f90
  Modules: 1
    - module modern_math_physics (vars=2, uses=0)
      Derived types: 3
        - type particle (fields=3, methods=0)
          Fields: 3
            - id:integer[0]
            - mass:real[0]
            - position:real[1]
        - type vector3 (fields=1, methods=0)
          Fields: 1
            - values:real[1]
        - type hidden_state (fields=1, methods=0)
          Fields: 1
            - code:integer[0]
      Procedures: 7
        - subroutine init_particle(p:type(particle)[0], pid:integer[0], mass:real[0], x:real[0], y:real[0], z:real[0])
        - function kinetic_energy(p:type(particle)[0], vx:real[0], vy:real[0], vz:real[0]) -> real[0]
        - subroutine scale_vector(v:real[1], alpha:real[0])
        - function dot3(a:real[1], b:real[1]) -> real[0]
        - subroutine fill_identity3(a:real[2])
        - subroutine normalize_particle(p:type(particle)[0])
        - subroutine hidden_proc(x:integer[0])
```

### Example 7: output written to file (`--out`)

When `--out` is provided, x2py writes files and does not print stage payloads to stdout.

Parse JSON to a specific file:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse --out report.json
```

Parse JSON adjacent to source (`basic_subroutine.json`):

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse --out
```

Semantic IR JSON to a specific file:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --semantics --out semantics.json
```

Generated `.pyi` to a specific file:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi --out module.pyi
```

Without an explicit filename, `--out` writes adjacent files next to each input
source: JSON for `--parse` and `--semantics`, `.pyi` for `--pyi`.

## Python script usage

### Example 1: parse a whole folder namespace

```python
from x2py import parse_fortran_project
from pathlib import Path

root = Path("tests/data/fortran/general")
files = [str(p) for p in root.rglob("*.f90")][:5]
project = parse_fortran_project(files)
print("files:", len(project.files))
print("modules:", len(project.modules))
```

Expected result:

- Returns a `FortranProject` aggregate for the folder.
- Includes dependency-aware ordering and cross-file kind/module resolution.

### Example 2: parse one file and inspect readiness

```python
from pathlib import Path
from x2py import (
    assess_semantic_wrap_readiness,
    fortran_file_to_semantic_modules,
    parse_fortran_file,
)

path = Path("tests/data/fortran/general/basic_subroutine.f90")
code = path.read_text()

parsed = parse_fortran_file(code, filename=str(path))
modules = fortran_file_to_semantic_modules(parsed, standalone_module_name=path.stem)
report = assess_semantic_wrap_readiness(modules, source=str(path))

print("procedures:", len(parsed.procedures))
print("wrappable:", report["wrappable"])
print("blockers:", report["why_not_wrappable"])
```

Expected result:

- `parsed` is a `FortranFile` aggregate with procedures/modules/types/interfaces/program units.
- `report` is produced from semantic IR and includes public API counts,
  semantic blockers, unit-level blockers, and final `wrappable` boolean.

If the parsed Fortran file cannot describe the wrapper interface completely,
generate a draft `.pyi`, edit it, then assess readiness from the edited stub:

```bash
python -m x2py solver.f90 --pyi --out solver.pyi
python -m x2py solver.pyi --wrap-readiness
```

The edited `.pyi` is the source of truth for readiness. It can declare derived
types with `class` stubs, literal compile-time constants with
`Final[...] = value`, and callback signatures with `Callable[[...], ...]`.

### Example 3: parse C from Python

```python
from x2py import parse_c_file, parse_c_project

header = parse_c_file("include/api.h")
print("functions:", [fn.name for fn in header.functions])
print("typedefs:", [typedef.name for typedef in header.typedefs])

project = parse_c_project(["src/api.c", "include/api.h"], include_dirs=["include"])
print("include graph:", project.include_graph)
print("header/source pairs:", project.header_source_pairs)
```

The same C entrypoints remain available from `c_parser`. Includes are recorded
as project facts and are not recursively parsed; supply every header that
should contribute declarations (or supply its containing directory). C
semantic conversion will be added through the semantic layer in a future
phase.

## Running tests

From repository root:

```bash
PYTHONPATH=. pytest -q
```

## Merging policy (soft enforcement)

This repository uses CI checks to validate parser behavior. As a project policy,
**do not merge pull requests unless all checks are green**.

Run key suites individually:

```bash
PYTHONPATH=. pytest -q tests/parser
PYTHONPATH=. pytest -q tests/semantics
PYTHONPATH=. pytest -q tests/pyi
```

### Refresh golden fixture JSON files

```bash
python tests/parser/fortran/generate_fortran_parser_goldens.py
```

Or update only specific fixture files:

```bash
python tests/parser/fortran/generate_fortran_parser_goldens.py tests/data/fortran/general/basic_subroutine.f90
```

During fixture test runs, you can also auto-update expected JSON in-place:

```bash
FORTRAN_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/parser --confcutdir=tests/
```

When parser model output changes, include the regenerated parser goldens and a
short explanation in the PR. For `.pyi` or semantic IR behavior changes, update
the corresponding fixtures under `tests/pyi/fixtures` or
`tests/semantics/fixtures`.

Semantic wrap-readiness corpus messages for the general, BLAS, LAPACK, and
SciFortran fixtures are regenerated separately:

```bash
python tests/semantics/generate_wrap_readiness_fixtures.py
```

This writes `tests/semantics/fixtures/wrap_readiness_messages.json`. The file is
a semantic readiness fixture, not a parser golden, even though Fortran fixtures
are used as input.

## Semantic parser structure

The parser exposes stable file/project entrypoints:

- `parse_fortran_file(...)` for one source (string or path) returning `FortranFile`.
- `parse_fortran_project(...)` for many sources returning `FortranProject`.

Wrap-readiness is intentionally outside the parser model. Use
`fortran_file_to_semantic_modules(...)` or `.pyi` parsing to produce semantic IR,
then call `assess_semantic_wrap_readiness(...)` on that semantic interface.

Internally, `FortranParser.visit_file` uses a recursive grammar-style
source-unit parser. The file is first sliced into direct
modules/submodules/programs/procedures/block-data/interfaces/types. Each unit
visitor then parses only its own substring, splits it into header,
specification, optional execution, and optional `contains` regions, and recurses
into direct child units where that grammar allows children. Shared declaration
helpers parse variables, procedure arguments/results, and type fields, then
push them into the active scope. Nested unit boundaries and placement outside
execution regions are checked even when they do not produce wrapper metadata.
Internal procedures inside a host procedure's `contains` block are
structurally sliced, then their declarations and bodies are skipped. After an
execution boundary is detected, procedure bodies and standalone included
execution fragments are intentionally skipped. Procedure-local interfaces are
retained for callback typing.
Parameter variables keep both `value` and serialized `symbolic_value` when the
parser has that information. `value` is literal/evaluated only; if an
initializer cannot be evaluated safely, `value` is `None` and
`symbolic_value` keeps the original expression.
Module-level parameters used in procedure argument shapes remain symbolic in
the signature while still being valid scoped references for readiness checks.

The semantics layer consumes `FortranFile`/`FortranModule` objects and projects them into language-independent semantic IR (`SemanticModule`, `SemanticFunction`, `SemanticClass`, `SemanticType`). This keeps the semantic API model independent from parser internals, matching the project goal that parser output is a helper and the semantic interface/IR is the source of truth.
For compiler-specific constants, use
`collect_semantic_compile_time_requirements(parsed)` to extract unresolved
values. With a configured Fortran compiler, pass those requirements to
`evaluate_fortran_type_requirements(config, requirements)` and provide the
returned dictionary to semantic conversion via `compile_time_values`. The CLI
does this automatically for Fortran semantic stages when compiler preprocessing
is active.

For Fortran `use` imports, the parser stores each explicit imported symbol as a
source/target mapping. A non-renamed `use iso_c_binding, only: c_int` maps
`source="c_int"` and `target=None`; a renamed
`use list_input, delete_input => delete_input_list` maps
`source="delete_input_list"` and `target="delete_input"`. The semantic layer
uses that information to emit Python stub imports such as
`from list_input import delete_input_list as delete_input`.

Fortran `use` dependencies are not parsed or wrapped recursively. If a
procedure refers to an imported derived type, semantic IR records its defining
module and represents the reference as an opaque handle unless the defining
module is explicitly part of the wrapping target. Explicitly supplied modules
share one wrapped-type registry, so the imported reference resolves to the
single class emitted by its owner module without being re-exported by the
importing module. Reachable include exposure is already handled separately by
the preprocessing include policy; a future dependency-expansion option would
apply specifically to recursive Fortran `use` traversal.

When an imported derived type remains external, `.pyi` generation emits an
owner-module dependency stub. For example, wrapping only `physics.f90` may
produce:

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

`python -m x2py physics.f90 --pyi --out` writes both files beside the source.
`load_pyi_modules(...)` loads a file set or directory, preserves opaque classes,
and reconciles imported references against edited owner stubs. Replacing the
opaque placeholder with a concrete edited class changes the semantic reference
from `representation="opaque"` to `representation="wrapped"`. Existing
`Annotated[...]` constraints also round-trip through this editable interface;
richer coercion syntax can be added to the same `.pyi` format later.

The same opaque-handle file-set model applies to C. A local forward declaration
such as `struct context;` emits `class context(Opaque): pass`. When a public C
header uses a struct from another explicitly supplied header, its generated
stub imports the class from that header's stub. A private included struct used
through a public pointer boundary emits an opaque owner-module dependency stub.
An unresolved C typedef is left unresolved rather than guessed to be opaque,
because its ABI may not be pointer-shaped.
