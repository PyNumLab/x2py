# Fortran parser reference (wrapper-focused subset)

This document defines the currently supported parser subset, expected behavior,
and practical usage from terminal and Python.

## 1) Supported features (comprehensive)

### 1.1 Source forms and preprocessing

- Free-form Fortran: `.f90`, `.f95`, `.f03`, `.f08`
- Fixed-form Fortran: `.f`, `.for`, `.ftn`
- Free/fixed comment stripping
- Continuation handling for both forms

### 1.2 Procedure parsing

- `subroutine` headers
- `function` headers
- Header modifiers: `pure`, `elemental`, `recursive`
- Function `result(...)` parsing (tolerant support for `results(...)`)

### 1.3 Declaration/argument parsing

- Intrinsic types: `integer`, `real`, `complex`, `logical`, `character`
- Kind extraction from declaration specs (`kind=...`)
- Attribute extraction:
  - `intent(in|out|inout)`
  - `optional`
  - `value`
  - `allocatable`
  - `pointer`
- Array extraction:
  - `dimension(...)`
  - variable-level shape syntax (`x(:)`, `x(n)`)

### 1.4 Modules, imports, and project context

- Module discovery
- Module variable extraction
- `use` extraction at module and procedure scope
- Propagation of module-level `use` imports into contained procedures
- Folder/project parsing with dependency-aware ordering
- Cross-file kind constant resolution (e.g., kinds modules)

### 1.5 Derived type parsing

- `type :: ... end type` discovery
- Type attributes (e.g., `abstract`)
- Inheritance (`extends(parent)`)
- Field extraction including shape/pointer/allocatable
- Type-bound procedures:
  - `procedure ... :: ...` bindings with attributes (e.g. `pass(self)`, `nopass`)
  - `generic ... :: name => target1, target2`

### 1.6 Readiness diagnostics

- Unsupported-pattern checks
- Unknown argument declaration reporting
- Final boolean readiness (`wrappable`)

## 2) Public API surface

- `parse_fortran_signatures`
- `parse_fortran_types`
- `parse_fortran_modules`
- `parse_fortran_project_signatures`
- `parse_fortran_namespace`
- `assess_wrap_readiness`

## 3) Terminal usage and expected outputs

### 3.1 Basic CLI invocation

```bash
python -m fortran_parser <path ...>
```

or (if installed as a console script):

```bash
fortran-parser <path ...>
```

`<path ...>` supports files and directories. Directories are recursively scanned
for `.f`, `.for`, `.ftn`, `.f90`, `.f95`, `.f03`, `.f08`.

### 3.2 Human-readable output example

Input Fortran (`tests/fcode/basic_subroutine.f90`):

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

Command:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90
```

Expected output shape:

```text
File: tests/fcode/basic_subroutine.f90
  Modules: 1
    - module m1 (vars=2, uses=0)
      Procedures: 1
        - subroutine add1(n:integer[0], x:real[1])
```

Interpretation:

- Parsed entities are counted per file.
- Free procedures (outside modules) are shown in top-level `Procedures`.
- Module-contained procedures are nested under each module.
- Empty sections are omitted from the human-readable report.

More complex example:

Input Fortran (`mixed_example.f90`):

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

### 3.3 JSON output example

Print JSON:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json
```

Write JSON:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json-out report.json
```

Print + write:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json --json-out report.json
```

Expected JSON layout:

- Top-level object keyed by input path
- Per-file payload with keys:
  - `signatures`
  - `types`
  - `modules`
  - `wrap_readiness`

## 4) Python usage and expected outputs

### 4.1 Parse folder namespace

```python
from fortran_parser import parse_fortran_namespace

namespace = parse_fortran_namespace("tests/fcode")
print(namespace.keys())
print(len(namespace["signatures"]))
```

Expected behavior:

- Recursively scans Fortran files.
- Resolves dependencies and module imports across files.
- Returns aggregate namespace parse output.

### 4.2 Parse single file and run readiness check

```python
from pathlib import Path
from fortran_parser import parse_fortran_signatures, assess_wrap_readiness

p = Path("tests/fcode/basic_subroutine.f90")
code = p.read_text()

signatures = parse_fortran_signatures(code, filename=str(p))
readiness = assess_wrap_readiness(code, filename=str(p))

print("signatures", len(signatures))
print("wrappable", readiness["wrappable"])
print("unsupported", readiness["unsupported_hits"])
```

Expected behavior:

- `signatures` is a normalized list of callable records.
- `readiness` includes counts, unsupported hits, unknown args, and `wrappable`.

## 5) Running tests

Run all tests:

```bash
PYTHONPATH=. pytest -q
```

Run parser-focused tests:

```bash
PYTHONPATH=. pytest -q tests/test_fortran_signature_parser.py
PYTHONPATH=. pytest -q tests/test_fortran_fixture_suite.py
PYTHONPATH=. pytest -q tests/test_cli.py
```

Update golden JSON fixtures:

```bash
python tests/fcode/generate_fortran_parser_goldens.py
```

Update selected fixture(s):

```bash
python tests/fcode/generate_fortran_parser_goldens.py tests/fcode/basic_subroutine.f90
```

In-test auto-update mode:

```bash
FORTRAN_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/test_fortran_fixture_suite.py --confcutdir=tests/
```

## 6) Scope note

This parser is intentionally wrapper-focused and not a complete Fortran front
end. Unsupported syntax should be surfaced through diagnostics/readiness output
for incremental parser extension.
