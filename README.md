# x2py

Standalone extraction of the Fortran parser used for wrapper-oriented signature
extraction.

[![Tests](https://github.com/PyNumLab/x2py/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/PyNumLab/x2py/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/PyNumLab/x2py/graph/badge.svg?token=QZRRCS5YO6)](https://codecov.io/gh/PyNumLab/x2py)


## What the parser handles

The parser is intentionally a robust subset parser (not a full Fortran compiler
front-end). Current handled coverage:

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
- **Readiness diagnostics**
  - Unsupported-pattern detection
  - Unknown argument declaration reporting
  - Final wrappability summary

## Public APIs

Public API:

- `parse_fortran_file(source_or_path, filename=None, macro_defines=None, encoding="utf-8") -> FortranFile`
- `parse_fortran_project(files, encoding="utf-8") -> FortranProject`
- `assess_wrap_readiness(code, filename=None) -> dict`

## Repository layout

Fortran source inputs live under `tests/data/fortran`. Stage-specific tests and expected fixtures live under `tests/parser`, `tests/semantics`, and `tests/pyi`.

The editable wrapper `.pyi` format is documented in
[`docs/pyi_format.md`](docs/pyi_format.md).

## Terminal usage

`x2py` exposes three stage flags:

- `--parse` for parser output and parse-stage diagnostics
- `--semantics` for semantic IR JSON
- `--pyi` for generated Python stub text

For parse output, `--show-vars` expands scope-level variables that are normally
summarized as `vars=N`. Use `--print-limit N` to keep large repeated sections
readable.

### Run from source tree

```bash
python -m x2py <path ...> --parse
```

### Run after installation

```bash
x2py <path ...> --parse
```

`<path ...>` can be one or more files and/or directories. Directories are
scanned recursively for: `.f`, `.for`, `.ftn`, `.f90`, `.f95`, `.f03`, `.f08`.

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
- `<file>.wrap_readiness`: readiness diagnostics

### Example 3: wrap-readiness summary

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse --wrap-readiness
```

This prints the wrappability status and blocker list for each input file.
The JSON readiness payload keeps `wrappable` at file level and includes
`unit_blockers` only for procedure/type/file units that own a blocker.

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
    position: Float64[Shape('3'), ORDER_F]

class vector3:
    values: Float64[Shape('3'), ORDER_F]

@private
class hidden_state:
    code: Int32

counter: Int32

hidden_scale: private[Float64]

@native_call([Return(0), Arg(0), Arg(1), Arg(2), Arg(3), Arg(4)])
def init_particle(
    pid: Int32,
    mass: Float64,
    x: Float64,
    y: Float64,
    z: Float64
) -> particle: ...

def kinetic_energy(
    p: particle,
    vx: Float64,
    vy: Float64,
    vz: Float64
) -> Float64: ...

def scale_vector(
    v: Float64[Shape(':'), ORDER_F],
    alpha: Float64
) -> Returns["v", Float64[Shape(':'), ORDER_F]]: ...

def dot3(
    a: Float64[Shape('3'), ORDER_F],
    b: Float64[Shape('3'), ORDER_F]
) -> Float64: ...

@native_call([Return(0)])
def fill_identity3() -> Float64[Shape('3', '3'), ORDER_F]: ...

def normalize_particle(
    p: particle
) -> Returns["p", particle]: ...

@private
def hidden_proc(
    x: Int32
) -> None: ...
```

This snapshot is also verified in `tests/pyi/test_pyi_printer_modern_example.py`.

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
from x2py import parse_fortran_file, assess_wrap_readiness

path = Path("tests/data/fortran/general/basic_subroutine.f90")
code = path.read_text()

parsed = parse_fortran_file(code, filename=str(path))
report = assess_wrap_readiness(code, filename=str(path))

print("procedures:", len(parsed.procedures))
print("wrappable:", report["wrappable"])
print("unknown args:", report["unknown_argument_types"])
```

Expected result:

- `parsed` is a `FortranFile` aggregate with procedures/modules/types/interfaces/program units.
- `report` includes counts, unsupported construct hits, unknown argument info,
  unresolved imported derived-type/kind dependencies, and final `wrappable`
  boolean.

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

## Semantic parser structure

The parser exposes stable file/project entrypoints:

- `parse_fortran_file(...)` for one source (string or path) returning `FortranFile`.
- `parse_fortran_project(...)` for many sources returning `FortranProject`.
- `assess_wrap_readiness(...)` for wrappability diagnostics.

Internally, `FortranParser.visit_file` uses a recursive grammar-style
source-unit parser. The file is first sliced into direct
modules/submodules/programs/procedures/block-data/interfaces/types. Each unit
visitor then parses only its own substring, splits it into header,
specification, optional execution, and optional `contains` regions, and recurses
into direct child units where that grammar allows children. Shared declaration
helpers parse variables, procedure arguments/results, and type fields, then
push them into the active scope. Procedure execution bodies and internal
subprograms are ignored for wrapper metadata; procedure-local interfaces are
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
values and pass a dictionary to semantic conversion via
`compile_time_values`.

For Fortran `use` imports, the parser stores each explicit imported symbol as a
source/target mapping. A non-renamed `use iso_c_binding, only: c_int` maps
`source="c_int"` and `target=None`; a renamed
`use list_input, delete_input => delete_input_list` maps
`source="delete_input_list"` and `target="delete_input"`. The semantic layer
uses that information to emit Python stub imports such as
`from list_input import delete_input_list as delete_input`.
