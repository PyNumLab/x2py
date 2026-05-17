# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`x2py` is a minimal Fortran signature parser that extracts procedure signatures, derived types, and module definitions from Fortran source files for Python wrapper generation. It is a robust subset parser — not a full Fortran compiler front-end — designed to produce clean, serializable data models.

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
python -m x2py path/to/file.f90 --parse
python -m x2py path/to/dir/ --parse --json
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
- `parser-reference-guard` — Fails if `fortran_parser/`, `tests/data/fortran/`, or `tests/parser/test_procedure_and_type_parsing.py` are changed without updating `parser_implementation_reference.md`. Bypass by adding the `require-parser-reference-update` label to the PR.

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.
