# minimal-fortran-parser

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

- `parse_fortran_signatures(code: str, filename: str | None = None)`
- `parse_fortran_types(code: str)`
- `parse_fortran_modules(code: str)`
- `parse_fortran_project_signatures(files: dict[str, str])`
- `parse_fortran_namespace(root: str)`
- `assess_wrap_readiness(code: str, filename: str | None = None)`

## Terminal usage

### Run from source tree

```bash
python -m fortran_parser <path ...>
```

### Run after installation

```bash
fortran-parser <path ...>
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
python -m fortran_parser tests/fcode/basic_subroutine.f90
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
python -m fortran_parser mixed_example.f90
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
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json
```

Expected JSON structure (top-level keyed by input path):

- `<file>.signatures`: parsed procedures
- `<file>.types`: parsed derived types
- `<file>.modules`: parsed modules
- `<file>.wrap_readiness`: readiness diagnostics

### Example 3: JSON output written to file

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json-out report.json
```

And print + write together:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json --json-out report.json
```

## Python script usage

### Example 1: parse a whole folder namespace

```python
from fortran_parser import parse_fortran_namespace

ns = parse_fortran_namespace("tests/fcode")
print("signatures:", len(ns["signatures"]))
print("types:", len(ns["types"]))
print("modules:", len(ns["modules"]))
```

Expected result:

- Returns a dictionary containing aggregate parser results for the folder.
- Includes dependency-aware ordering and cross-file kind/module resolution.

### Example 2: parse one file and inspect readiness

```python
from pathlib import Path
from fortran_parser import parse_fortran_signatures, assess_wrap_readiness

path = Path("tests/fcode/basic_subroutine.f90")
code = path.read_text()

sigs = parse_fortran_signatures(code, filename=str(path))
report = assess_wrap_readiness(code, filename=str(path))

print("procedures:", len(sigs))
print("wrappable:", report["wrappable"])
print("unknown args:", report["unknown_arguments"])
```

Expected result:

- `sigs` is a list of normalized procedure signatures.
- `report` includes counts, unsupported construct hits, unknown argument info,
  and final `wrappable` boolean.

## Running tests

From repository root:

```bash
PYTHONPATH=. pytest -q
```

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
