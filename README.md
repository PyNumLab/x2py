# minimal-fortran-parser

Standalone extraction of the Fortran parser from this repository.

## APIs

- `parse_fortran_signatures`
- `parse_fortran_types`
- `parse_fortran_modules`
- `parse_fortran_project_signatures`
- `parse_fortran_namespace`
- `assess_wrap_readiness`

## Quick start

```python
from fortran_parser import parse_fortran_namespace

ns = parse_fortran_namespace("/path/to/fortran/project")
print(len(ns["signatures"]))
```

## Command-line usage

You can run the parser directly from the terminal to inspect one or many Fortran
files without writing Python code.

### Run from source tree

```bash
python -m fortran_parser <path ...>
```

### Run after installation

```bash
fortran-parser <path ...>
```

`<path ...>` can be:

- one or more Fortran files
- one or more directories (directories are scanned recursively for: `.f`, `.for`, `.ftn`, `.f90`, `.f95`, `.f03`, `.f08`)

### Default output (human-readable)

By default, the CLI prints a readable summary per file:

- number of parsed procedures
- each procedure signature in compact form
- number of derived types
- number of modules
- wrap-readiness summary (`Wrappable: True/False`)

Example:

```text
File: tests/fcode/basic_subroutine.f90
  Procedures: 1
    - subroutine add1(n:integer[0], x:real[1])
  Derived types: 0
  Modules: 1
    - module m1 (vars=2, uses=0)
  Wrappable: True
```

### JSON output options

Print JSON to stdout:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json
```

Write JSON to a file:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json-out report.json
```

Do both at once:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json --json-out report.json
```

### What to expect in JSON

The top-level JSON object is keyed by input file path. For each file, the value contains:

- `signatures`: parsed procedures
- `types`: parsed derived types
- `modules`: parsed modules
- `wrap_readiness`: readiness diagnostics from `assess_wrap_readiness`

This output is suitable for parser validation and automated checks.
