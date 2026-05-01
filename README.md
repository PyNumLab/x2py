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
