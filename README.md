# minimal-x2py

Standalone extraction of the Fortran parser used for wrapper-oriented signature
extraction.

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
  - Propagation of module-level `use` into contained procedures
  - Cross-file kind resolution when parsing a namespace/project
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

## Parser organization notes

`fortran_parser/parser.py` is now intentionally organized into clearly labeled
sections so maintainers can navigate the file by concern instead of by history:

- Regex/constants and parser-wide type aliases
- Module-level helper blocks (source-form rules, preprocessor logic,
  diagnostics, shape evaluation, compile-time expression resolution,
  dependency ordering)
- `FortranParser` internals grouped by domain:
  - signature/declaration parsing
  - module-variable parsing
  - file/project orchestration
  - program-unit parsers (types, modules, interfaces, submodules, programs,
    block-data)
  - public API wrappers (`parse_file`, `parse_project`,
    `assess_wrap_readiness`)
- Thin module-level convenience wrappers that delegate to a shared parser
  instance

This was a structural readability refactor only: behavior and public return
models are unchanged.

## Terminal usage

### Run from source tree

> Parsing is a stage now, so pass `--parse` when you want parser output.

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

Fortran input (`tests/fcode/basic_subroutine.f90`):

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
python -m x2py tests/fcode/basic_subroutine.f90 --parse
```

Expected style of output:

```text
File: tests/fcode/basic_subroutine.f90
  Modules: 1
    - module m1 (vars=2, uses=0)
      Procedures: 1
        - subroutine add1(n:integer[0], x:real[1])
```

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

> JSON output is currently supported only for the parsing stage (`--parse`).

```bash
python -m x2py tests/fcode/basic_subroutine.f90 --parse --json
```

Expected JSON structure (top-level keyed by input path):

- `<file>.signatures`: parsed procedures
- `<file>.types`: parsed derived types
- `<file>.modules`: parsed modules
- `<file>.wrap_readiness`: readiness diagnostics

### Example 3: wrap-readiness summary

```bash
python -m x2py tests/fcode/basic_subroutine.f90 --wrap-readiness
```

The summary prints `Wrappable: yes` when no blockers are detected. If the
answer is `Wrappable: no`, it prints a `Why not wrappable` section with the
blocking diagnostics, such as unresolved imported derived types or unresolved
symbolic kinds.

### Example 5: semantic IR JSON output

```bash
python -m x2py tests/fcode/basic_subroutine.f90 --semantics
```

This prints semantic conversion payload per file, including:

- `semantic_modules`: semantic module/class/function/type metadata
- `pyi`: generated `.pyi` text associated with those semantic modules

### Example 6: print generated `.pyi` text

```bash
python -m x2py tests/fcode/basic_subroutine.f90 --pyi
```

This prints a per-file section followed by the generated Python stub text.


### Example 7: modern Fortran module -> `.pyi` (reproducible fixture)

The repository includes a richer modern-Fortran fixture at:

- `tests/semantics/fixtures/modern_pyi_example.f90`

Generate its stubs:

```bash
python -m x2py tests/semantics/fixtures/modern_pyi_example.f90 --pyi
```

Illustrative rich `.pyi` output (showing derived types, module variables, arrays,
and visibility markers):

```python
class particle:
    id: Int32
    mass: Float64
    position: Float64[Shape('3'), FortranContiguous]

counter: Int32
hidden_scale: Float64  # private

def init_particle(
    p: particle,
    pid: Int32,
    mass: Float64,
    x: Float64,
    y: Float64,
    z: Float64
) -> None: ...

def kinetic_energy(
    p: particle,
    vx: Float64,
    vy: Float64,
    vz: Float64
) -> Float64: ...

def scale_vector(
    v: Float64[Shape(':'), FortranContiguous],
    alpha: Float64
) -> None: ...

def dot3(
    a: Float64[Shape('3'), FortranContiguous],
    b: Float64[Shape('3'), FortranContiguous]
) -> Float64: ...

def fill_identity3(
    a: Float64[Shape('3', '3'), FortranContiguous]
) -> None: ...

@private
def hidden_proc(
    x: Int32
) -> None: ...
```

This snapshot is also verified in `tests/semantics/test_pyi_printer_modern_example.py`.

Parse output for the same fixture now includes the derived type definition and field list:

```bash
python -m x2py tests/semantics/fixtures/modern_pyi_example.f90 --parse
```

```text
File: tests/semantics/fixtures/modern_pyi_example.f90
  Modules: 1
    - module modern_math_physics (vars=0, uses=0)
      Derived types: 1
        - type particle (fields=3, methods=0)
          Fields: 3
            - id:integer[0]
            - mass:real[0]
            - position:real[1]
      Procedures: 5
        - subroutine init_particle(p:type(particle)[0], pid:integer[0], mass:real[0], x:real[0], y:real[0], z:real[0])
```

### Example 4: output written to file (`--out`)

When `--out` is provided, x2py writes files and does not print stage payloads to stdout.

Parse JSON to a specific file:

```bash
python -m x2py tests/fcode/basic_subroutine.f90 --parse --out report.json
```

Parse JSON adjacent to source (`basic_subroutine.json`):

```bash
python -m x2py tests/fcode/basic_subroutine.f90 --parse --out
```

Semantic IR JSON to a specific file:

```bash
python -m x2py tests/fcode/basic_subroutine.f90 --semantics --out semantics.json
```

Generated `.pyi` to a specific file:

```bash
python -m x2py tests/fcode/basic_subroutine.f90 --pyi --out module.pyi
```

## Python script usage

### Example 1: parse a whole folder namespace

```python
from fortran_parser import parse_fortran_project
from pathlib import Path

root = Path("tests/fcode")
files = [str(p) for p in root.rglob("*.f90")][:5]
project = parse_fortran_project(files)
print("files:", len(project.files))
print("modules:", len(project.modules))
```

Expected result:

- Returns a dictionary containing aggregate parser results for the folder.
- Includes dependency-aware ordering and cross-file kind/module resolution.

### Example 2: parse one file and inspect readiness

```python
from pathlib import Path
from fortran_parser import parse_fortran_file, assess_wrap_readiness

path = Path("tests/fcode/basic_subroutine.f90")
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
PYTHONPATH=. pytest -q tests/test_fortran_signature_parser.py
PYTHONPATH=. pytest -q tests/test_fortran_fixture_suite.py
PYTHONPATH=. pytest -q tests/test_cli.py
```

### Refresh golden fixture JSON files

```bash
python tests/fcode/generate_fortran_parser_goldens.py
```

Or update only specific fixture files:

```bash
python tests/fcode/generate_fortran_parser_goldens.py tests/fcode/basic_subroutine.f90
```

During fixture test runs, you can also auto-update expected JSON in-place:

```bash
FORTRAN_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/test_fortran_fixture_suite.py --confcutdir=tests/
```

## Semantic parser structure

The parser exposes stable file/project entrypoints:

- `parse_fortran_file(...)` for one source (string or path) returning `FortranFile`.
- `parse_fortran_project(...)` for many sources returning `FortranProject`.
- `assess_wrap_readiness(...)` for wrappability diagnostics.

The semantics layer consumes `FortranFile`/`FortranModule` objects and projects them into language-independent semantic IR (`SemanticModule`, `SemanticFunction`, `SemanticClass`, `SemanticType`). This keeps the semantic API model independent from parser internals, matching the project goal that parser output is a helper and the semantic interface/IR is the source of truth.
