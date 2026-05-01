# Building a minimal Fortran parser for an f2py-like wrapper tool

This guide focuses on a **self-contained minimal parser** (no external Fortran parser frameworks) that extracts enough information to generate Python wrappers for common Fortran procedures.

## Scope and philosophy

The goal is not full Fortran compliance. The goal is a robust subset parser for wrapper generation:

- free-form Fortran source
- module/subroutine/function declarations
- declaration statements for arguments/results
- `intent`, `optional`, `value`, `dimension`, `allocatable`, `pointer`
- `use` statements needed to resolve kind constants

Anything outside this subset should return a clear "unsupported syntax" diagnostic.

This parser is intentionally **not** a complete Fortran 77→latest compiler front-end.
It is a wrapper-focused subset parser and should be paired with a readiness check.

The sections below enumerate the handled features and data extracted for wrappers so behavior can be tracked through version control diffs.

## Comprehensive handled coverage

### Source forms and preprocessing

- Free-form Fortran (`.f90`, `.f95`, `.f03`, `.f08`).
- Fixed-form Fortran (`.f`, `.for`, `.ftn`) including classic continuation in column 6.
- Comment stripping for free/fixed forms.
- Continuation handling for both forms.

### Procedures and callable signatures

- `subroutine` and `function` headers.
- Procedure prefixes/attributes in headers: `pure`, `elemental`, `recursive`.
- Function results via `result(...)` (and tolerant `results(...)` parsing).
- Procedure-level `use` imports, plus module-level `use` imports propagated to contained procedures.
- Argument declaration parsing with:
  - intrinsic base types (`integer`, `real`, `complex`, `logical`, `character`)
  - kind extraction (`kind=...`)
  - `intent(in|out|inout)`
  - `optional`, `value`, `allocatable`, `pointer`
  - `dimension(...)` and variable-level array shape (`x(:)`, `x(n)`).

### Module-level parsing

- Module discovery and module-level variable declarations.
- Module-level `use` dependency extraction.
- Namespace parsing of an entire folder with file dependency graph and deterministic ordering.
- Cross-file kind resolution for imported module parameters (e.g. `rk` from a kinds module).

### Multi-file project and folder parsing

- `parse_fortran_project_signatures(files: dict[str, str])` parses a provided file map and resolves imported kind parameters across files.
- `parse_fortran_namespace(root)` scans a folder recursively for Fortran files (`.f`, `.for`, `.ftn`, `.f90`, `.f95`, `.f03`, `.f08`) and parses it as one namespace.
- Namespace parsing builds:
  - module-to-file ownership mapping
  - file dependency graph from `use` relations
  - deterministic dependency-aware parse ordering (topological where possible, stable fallback for cycles)
- Module-level `use` imports are propagated to contained procedures so imports declared at module scope are still visible during signature extraction.

### Derived datatypes

- `type :: ... end type` discovery.
- Type attributes (e.g. `abstract`) and inheritance (`extends(parent_type)`).
- Field extraction (intrinsic + `type(...)` fields), including shape/pointer/allocatable metadata.
- Type-bound procedures from `contains` blocks:
  - `procedure ... :: ...` bindings with parsed binding attributes (e.g. `pass(self)`, `nopass`).
  - `generic ... :: name => target1, target2` bindings (including operator-like names such as `assignment(=)`).

### Diagnostics and readiness checks

- `assess_wrap_readiness(...)` report with:
  - parsed entity counts
  - unsupported-construct hits based on known pattern checks
  - unknown argument declarations
  - final `wrappable` boolean.

## Output model (normalized signature)

For each exported callable, emit:

- identity: module name (optional), procedure name
- kind: `function` or `subroutine`
- ordered argument list:
  - name
  - base type (`integer|real|complex|logical|character`)
  - kind (raw expression text is acceptable initially)
  - rank and shape spec (if any)
  - intent (`in|out|inout|unknown`)
  - flags (`optional`, `value`, `allocatable`, `pointer`)
- function result metadata (for functions)
- procedure attributes (e.g. `pure`, `elemental`, `bind(c)` if parsed)

This schema should be parser-internal-agnostic and directly consumable by wrapper codegen.

## Minimal parser architecture (no external parsers)

Use a straightforward **three-stage pipeline**:

1. **Preprocessor-lite scanner**
   - strip comments
   - join continuation lines (`&`)
   - normalize case for keywords while preserving identifiers
2. **Line-based declaration parser**
   - detect block boundaries (`module`, `contains`, `subroutine`, `function`, `end`)
   - parse procedure headers (names + argument list)
   - parse declaration lines into type + attributes + variable list
3. **Semantic collector**
   - build per-procedure symbol table
   - merge header arguments with declaration metadata
   - produce normalized signature records

Keep all parsing deterministic and regex/token based; avoid trying to parse full executable statements.

## Grammar subset to implement first

Implement recognition for these forms first:

- Procedure headers:
  - `subroutine name(a,b,c)`
  - `pure subroutine name(a,b)`
  - `function f(x) result(y)`
- Type declarations:
  - `real(kind=8), intent(in) :: x`
  - `integer, dimension(:), intent(inout) :: a`
  - `character(len=*), intent(in) :: s`
- Multi-variable declarations:
  - `real, intent(in) :: x, y, z`
- `use` statements:
  - `use iso_c_binding, only: c_int, c_double`

Start with this subset, then expand only from real failures in your test corpus.

## Suggested implementation modules

A simple project structure:

- `lexer.py`
  - comment stripping
  - continuation folding
  - token utilities
- `fortran_subset_parser.py`
  - block traversal
  - header/declaration parsers
- `signature_model.py`
  - dataclasses for normalized signatures
- `extract_signatures.py`
  - public API: parse file(s) → list/signature JSON

A compact hand-written parser is easier to debug than a large generalized grammar for this use case.

## Error handling rules

- Unsupported construct inside a target procedure: emit a structured warning with file+line.
- Missing declaration for an argument: keep argument with `type=unknown` and continue.
- Ambiguous parse: fail the procedure, not the whole file, unless configured as strict.

This allows incremental adoption on real-world codebases.

## Validation strategy

Use a golden-fixture approach:

- `tests/parser/tests/*.f*` with small focused inputs
- `tests/parser/tests/*.json` with normalized signatures
- regression test compares produced JSON to expected JSON

Add fixtures every time a user file breaks parsing.

### Auto-updating expected outputs

To avoid manually writing JSON expected files, use:

- `python tests/parser/generate_fortran_parser_goldens.py`
- `python tests/parser/generate_fortran_parser_goldens.py basic_subroutine.f90`

This script scans `tests/parser/tests/*.f*` by default, parses each file, and rewrites
`tests/parser/tests/<fixture>.json`.
If file names are provided as arguments, it updates only those fixtures.

For convenience during development, the fixture test also supports:

- `FORTRAN_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/parser/test_fortran_fixture_suite.py --confcutdir=tests/parser`

In this mode the test updates golden files in-place instead of asserting diffs.

## Wrap-readiness check

Use `assess_wrap_readiness(code, filename=None)` before wrapper generation.
It reports:

- number of parsed procedures/types/modules
- unsupported constructs detected by pattern checks
- arguments whose declarations could not be typed (`base_type = unknown`)
- a boolean `wrappable` summary

This gives an explicit signal when a file likely needs parser extensions before
automatic wrapping is safe.

## First milestone checklist

- [ ] parse module-level procedures + contained procedures
- [ ] parse argument declarations with type/kind/intent/rank/optional
- [ ] support function result variables
- [ ] emit stable JSON signatures
- [ ] cover at least 20 fixture files across common scientific signatures

With this milestone, you can generate wrappers for a useful subset of Fortran APIs while keeping the parser small and maintainable.

