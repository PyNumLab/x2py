# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`pyccel-f2py` is a minimal Fortran signature parser that extracts procedure signatures, derived types, and module definitions from Fortran source files for Python wrapper generation. It is a robust subset parser — not a full Fortran compiler front-end — designed to produce clean, serializable data models.

## Commands

```bash
# Run all tests
PYTHONPATH=. pytest -q

# Run a single test file
PYTHONPATH=. pytest -q tests/test_fortran_signature_parser.py

# Run a single test by name
PYTHONPATH=. pytest -q -k "test_name"

# Regenerate golden JSON files after intentional parser changes
FORTRAN_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/test_fortran_fixture_suite.py

# Run the CLI
python -m fortran_parser path/to/file.f90
python -m fortran_parser path/to/dir/ --json
```

## Architecture

### Core modules (`fortran_parser/`)

- **lexer.py** — Preprocessing stage: strips comments, folds continuation lines, detects source form (free vs fixed). Called before any parsing.
- **models.py** — Dataclass models: `FortranVariable`, `FortranArgument`, `FortranProcedureSignature`, `FortranDerivedType`, `FortranInterface`, `FortranModule`. These are the output types of all parsers.
- **parser.py** — The core (1200+ lines). Contains all parsing logic as standalone functions:
  - `parse_fortran_signatures()` — single-file procedure extraction (state-machine line iterator)
  - `parse_fortran_types()` / `parse_fortran_modules()` / `parse_fortran_interfaces()` — type/module/interface extraction
  - `parse_fortran_project_signatures()` — cross-file parsing with kind/dimension resolution
  - `parse_fortran_namespace()` — whole-directory parsing with dependency ordering
  - `assess_wrap_readiness()` — diagnostic analysis; unsupported constructs are tracked, not raised as errors
- **type_resolver.py** — Extracts kind specifications from type declarations.
- **utils.py** — `detect_source_form()`, `split_csv()` (comma-split respecting parenthesis nesting).
- **cli.py** — CLI: human-readable tree output and JSON output.

### Parsing design

The parser uses regex-based pattern matching on preprocessed (lexed) lines. `parse_fortran_signatures()` is a state machine that tracks whether it is inside a procedure body, derived type, interface block, or module. Unsupported Fortran constructs (polymorphic types, coarrays, procedure pointers, etc.) are recorded in a wrap-readiness report rather than causing failures.

Cross-file kind resolution happens in a second pass after initial signature extraction, using module-level `PARAMETER` constants to resolve symbolic kind/dimension values.

### Test structure

- **test_fortran_signature_parser.py** — Unit tests for specific parser behaviours (intent, kind, rank, fixed-form, use statements, derived types).
- **test_fortran_fixture_suite.py** — Golden-file regression tests. Parses fixture files in `tests/fcode/` and compares against expected `.json` files. Update goldens with `FORTRAN_PARSER_UPDATE_GOLDENS=1`.
- **test_cli.py** — CLI output tests.

### CI

- `tests.yml` — Runs `pytest -q` on Python 3.10, 3.11, 3.12.
- `parser-reference-guard` — Fails if `fortran_parser/`, `tests/fcode/`, or `tests/test_fortran_signature_parser.py` are changed without updating `parser_implementation_reference.md`. Bypass by adding the `require-parser-reference-update` label to the PR.
