# x2py

Wrapper-oriented parser and semantic-interface tooling for Fortran, with a C
frontend for declaration/signature extraction needed by wrapper generation.

[![Tests](https://github.com/PyNumLab/x2py/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/PyNumLab/x2py/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/PyNumLab/x2py/graph/badge.svg?token=QZRRCS5YO6)](https://codecov.io/gh/PyNumLab/x2py)

## What It Does

x2py turns native source interfaces into structured parser output, semantic IR,
generated `.pyi` stubs, and wrap-readiness reports.

The project is intentionally wrapper-oriented. It does not aim to be a full
compiler frontend. The parsers preserve the declarations, signatures, type
facts, source locations, include/use relationships, diagnostics, and semantic
metadata needed for later wrapper generation.

## Documentation

Start with the documentation that matches your role:

- [User documentation](docs/user.md): CLI usage, Python API usage, `.pyi` stub
  format, datatype mappings, examples, readiness reports, and user
  responsibilities.
- [Developer documentation](docs/developer.md): implementation map, parser and
  semantic contracts, how to add features, fixture maintenance, and focused
  test commands for each project area.

Additional references:

- [Documentation index](docs/README.md)
- [C parser reference](docs/c_parser.md)
- [Fortran parser reference](docs/fortran_parser.md)
- [Semantic IR and `.pyi` reference](docs/semantics.md)
- [Wrapper design notes](docs/wrapper_design_notes.md)
- [Diagnostic codes](docs/diagnostic_codes.md)

## Quick Start

Parse a Fortran source file:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
```

Generate a `.pyi` interface draft:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
```

Check whether a source file or edited `.pyi` has enough semantic information
for wrapping:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
python -m x2py solver.pyi --wrap-readiness
```

Parse C declarations through compiler preprocessing:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --parse --json
```

Use compiler and include flags when source depends on macros, conditional
branches, or target headers:

```bash
python -m x2py include/api.h --language c --parse \
  --compiler clang \
  -I include \
  -D API_EXPORT=
```

## Python API

The public Python entrypoints are exposed from `x2py`:

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
)
```

See [User Documentation](docs/user.md#python-api-workflows) for practical API
examples and [Developer Documentation](docs/developer.md) for the internal
contracts behind those entrypoints.

## Repository Layout

- `fortran_parser/`: Fortran parser frontend.
- `c_parser/`: C parser frontend.
- `semantics/`: semantic IR conversion, `.pyi` loading/printing, datatype
  mapping, and wrap-readiness checks.
- `x2py/`: package entrypoints and CLI integration.
- `tests/`: parser, semantic, CLI, and fixture tests.
- `docs/`: user, developer, parser, semantic, and design references.

## Running Tests

From the repository root:

```bash
PYTHONPATH=. pytest -q
```

Focused developer commands for C parser changes, Fortran parser changes,
semantic changes, CLI changes, fixture regeneration, linting, and coverage are
listed in [Developer Documentation](docs/developer.md#testing-map).
