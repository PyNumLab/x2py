# Parser implementation reference (feature inventory)

This is an implementation-level checklist of what this repository already handles,
intended as a transfer document for re-implementing the same architecture for
another source language.

## 1) End-to-end capabilities

- Parse individual Fortran sources into normalized callable signatures.  
- Parse derived types (including inheritance and type-bound procedures).  
- Parse modules (including module `use` imports and module variables).  
- Parse interfaces and procedures declared inside interfaces.  
- Parse whole directories/namespaces with dependency-aware ordering.  
- Resolve compile-time symbols used in type kinds and array shapes, both local
  and cross-file via imported modules.  
- Produce wrap-readiness diagnostics (`unsupported_constructs`, unknown
  argument declarations, wrappable boolean).  
- Provide CLI output in both human-readable tree form and JSON form.  

## 2) Language coverage actually implemented

### 2.1 Source forms, lexing, and preprocessing

- Free-form Fortran suffixes: `.f90`, `.f95`, `.f03`, `.f08`.  
- Fixed-form suffixes: `.f`, `.for`, `.ftn`.  
- Comment stripping and continuation folding via preprocessing stage.  
- Fortran-77 fixed-form continuation support validated by tests.  

### 2.2 Procedures

- `subroutine` headers.  
- `function` headers.  
- Header attributes: `pure`, `elemental`, `recursive`.  
- `bind(c)` attribute detection in headers/tail.  
- `result(...)` (and tolerant `results(...)`) parsing for function results.  
- Procedure arguments retained in declared order.  
- Local variables are ignored for signature argument lists.  
- Internal procedures inside `contains` blocks are ignored when parsing a
  parent routine signature.  
- Interface-contained procedures flagged as `in_interface`.  

### 2.3 Types, arguments, declarations

- Intrinsic bases: `integer`, `real`, `complex`, `logical`, `character`.  
- Derived argument declarations through `type(<name>)`.  
- Declaration attributes extracted:
  - `intent(in|out|inout)`
  - `optional`
  - `value`
  - `allocatable`
  - `pointer`
- Rank/shape extraction from:
  - declaration-level `dimension(...)`
  - variable-level inline shape `x(...)`
- `kind=...` extraction and assignment into argument/result metadata.  

### 2.4 Compile-time symbol and expression resolution

- Local `parameter` constants collected inside procedure scope.  
- Module-scope `parameter` constants collected in module specification part.  
- `use <module>, only: ...` symbol import maps collected and attached to
  procedures/modules.  
- Signature kind expressions resolved transitively (symbol -> symbol -> value).  
- Shape expressions resolved using available symbol dictionary.  
- Namespace/project parsing resolves cross-file kinds and dimensions after
  dependency ordering.  

### 2.5 Modules

- Module discovery with module context assignment to contained entities.  
- Module-level `use` dependencies parsed (including `only` symbol lists).  
- Module variables extracted from specification part declarations.  
- Module records enriched with child entities:
  - contained procedures
  - contained derived types
  - contained interfaces
- Module-level `use` imports propagated to contained procedures at parse time.  

### 2.6 Derived types

- `type :: name ... end type` discovery.  
- Type attributes list extraction (e.g., `abstract`).  
- `extends(parent)` extraction.  
- Same-file parent linking (`extends` string replaced with parent object when
  parent type is parsed in same file).  
- Field extraction:
  - intrinsic and derived fields
  - field rank/shape
  - pointer/allocatable flags
- Type-bound procedure bindings:
  - `procedure :: m1, m2`
  - binding attribute capture from declaration side
- Generic type-bound bindings:
  - `generic ... :: name => target1, target2`

### 2.7 Interfaces

- Named and unnamed interface blocks detected.  
- Procedures parsed inside interface blocks.  
- Interface objects associated to surrounding module when present.  

### 2.8 Wrap-readiness analysis

- Unsupported construct patterns explicitly scanned:
  - polymorphic `class(...)`
  - `select type`
  - coarray forms
  - `procedure, pointer`
  - `type(c_ptr)`
- Unknown argument declaration tracking (`base_type == "unknown"`).  
- Summary report fields:
  - `n_signatures`, `n_types`, `n_modules`
  - `unsupported_constructs`
  - `unknown_argument_types`
  - `wrappable`

## 3) Output/data model behavior

- Core parsing APIs return typed model objects (procedures, arguments, modules,
  types, interfaces, variables).  
- Namespace parse returns aggregate dictionary with:
  - ordered file list
  - file dependency graph
  - module-to-file index
  - merged modules/types/signatures
- CLI JSON output emits per-file buckets for signatures, types, modules,
  readiness report.  
- CLI human output prints tree-like structure grouped by file/module/procedure.  

## 4) Test strategy implemented (current workflow)

### 4.1 Day-to-day test command

Primary regression command used now:

- `PYTHONPATH=. pytest -q tests/test_fortran_signature_parser.py tests/test_fortran_fixture_suite.py tests/test_cli.py`

This single command runs all parser/unit checks, fixture/golden checks,
large corpus parse checks (BLAS/LAPACK fixture parsing), and CLI checks.

### 4.2 Unit-style parser tests (`tests/test_fortran_signature_parser.py`)

Covers, among others:
- intent/kind/rank extraction for routine arguments
- function result parsing + `use` extraction
- fixed-form parsing and interface detection
- cross-file kind resolution from imported module parameters
- derived type fields and method detection
- module variable and `use` parsing
- module children attachment (procedures/types/interfaces)
- ignoring local vars in external signatures
- ignoring internal procedures in `contains`
- local parameter propagation into argument kinds
- compile-time shape expression evaluation helpers
- shape symbol collection helpers
- readiness diagnostics and unsupported detection

### 4.3 Fixture and corpus regression (`tests/test_fortran_fixture_suite.py`)

- Golden fixture tests:
  - parse curated fixtures under `tests/fcode/*.f90` and `tests/fcode/*.f`
  - compare normalized parse output against sibling JSON goldens
- Large corpus parse-only sanity tests:
  - parse BLAS source fixtures under `tests/fcode/blas`
  - parse LAPACK source fixtures under `tests/fcode/lapack`

The corpus checks provide broad “does it parse?” coverage over many real-world
fixed/free-form Fortran files without requiring full golden outputs for each.

### 4.4 Golden regeneration support

- Script provided: `tests/fcode/generate_fortran_parser_goldens.py`.
- Use when parser behavior is intentionally changed and golden JSON needs
  updating.
- Optional in-test auto-update flow is also supported:
  - `FORTRAN_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/test_fortran_fixture_suite.py --confcutdir=tests/`

### 4.5 CLI tests (`tests/test_cli.py`)

Validates command-line behavior for:
- path expansion
- human-readable output
- JSON output
- JSON file writing
- module/free-procedure name collision handling

## 5) Repository/file structure reference

- `fortran_parser/lexer.py`
  - line preprocessing, source-form handling, continuation/comment normalization.
- `fortran_parser/parser.py`
  - main grammar subset parser and orchestration functions.
- `fortran_parser/type_resolver.py`
  - kind extraction and symbol/expression helpers.
- `fortran_parser/models.py`
  - parser data structures / model schema.
- `fortran_parser/utils.py`
  - shared text utilities (e.g., CSV-like splitting used by declarations).
- `fortran_parser/cli.py`
  - CLI argument parsing and report formatting.
- `fortran_parser/__main__.py`
  - `python -m fortran_parser` entry point.
- `tests/test_fortran_signature_parser.py`
  - focused behavior tests per feature.
- `tests/test_fortran_fixture_suite.py`
  - fixture-vs-golden regression checks.
- `tests/test_cli.py`
  - end-user command behavior tests.
- `tests/fcode/*.f90`, `*.f`
  - fixture Fortran samples.
- `tests/fcode/*.json`
  - fixture golden parse outputs.
- `tests/fcode/generate_fortran_parser_goldens.py`
  - golden regeneration tool.

## 6) Reimplementation checklist for another language

If you want another agent to reproduce the same architecture for a new language,
ask it to implement each of these layers explicitly:

1. Preprocessor/lexer layer for source forms, comments, continuations.  
2. Procedure signature parser (headers, args, attributes, result handling).  
3. Declaration parser for types/intent/shape/flags.  
4. Module/package parser with import/use tracking.  
5. Composite type parser (fields, inheritance, bound methods/generics).  
6. Interface/contract block parser.  
7. Symbol resolver for local and cross-file compile-time constants.  
8. Project namespace parser with dependency ordering.  
9. Readiness validator with unsupported-pattern rules + unknown type checks.  
10. CLI with tree output + JSON output + file emission.  
11. Unit tests per feature + fixture/golden regression suite + golden
    regeneration script.  


## 7) Scope handling and valued-variable mechanics (explicit)

These behaviors are easy to miss, but they are core to correctness and are
implemented today:

- **Procedure argument scope isolation**: declarations only apply to symbols
  belonging to the current procedure header argument/result symbol table;
  unrelated locals do not overwrite signature arguments.
- **Module specification scope tracking**: module `parameter` collection is
  restricted to the module specification part and stops at `contains`, avoiding
  leakage from executable regions.
- **Interface scope tracking**: procedures parsed inside `interface ... end
  interface` are represented separately and flagged as interface procedures.
- **Internal procedure scope protection**: nested procedures in a host
  `contains` block are not merged into the host routine signature.
- **Name-reuse safety across scopes**: fixtures/tests cover same identifier
  reuse in separate host/internal/type scopes to ensure no cross-scope symbol
  pollution.
- **Valued variables map**: compile-time constants are preserved as
  `FortranVariable(name, value)` records in signature metadata.
- **Expression normalization using valued variables**: argument kinds and shape
  expressions are rewritten using the resolved valued-variable map, including
  transitively dependent symbols.
- **Imported constant merge policy**: local/module/imported constants are merged
  into a single symbol-value dictionary with precedence that preserves explicit
  procedure-local definitions.

## 8) Implementation timeline highlights from repository history

A condensed history of important parser capabilities added over time (from
`git log`):

- Improved argument declaration parsing plus shape/derived coverage.
- Added assumed-shape bounds and derived-argument fixture coverage.
- Added compile-time shape-expression resolution from parameters.
- Added symbolic shape-evaluation API for externally supplied symbol values.
- Restricted module-parameter collection to module specification scope.
- Fixed deep and cyclic compile-time dependency resolution behavior.
- Added comprehensive compile-time expression fixtures.
- Added terminal CLI and documented expected outputs.
- Added interface nodes and module-tree integration.
- Simplified/strengthened golden serialization + generator flow.
- Improved compile-time argument expression resolution and local-variable
  distinction.
- Added same-file derived-type parent object linking (`extends`).
- Added valued-variable support and tests.
- Refined CLI tree output (omit empty/internal sections; stable module
  procedure grouping).
- Added tests/fixtures for same-name reuse across different scopes.

## 9) Pull-request maintenance policy for this reference

To keep this document useful as an implementation transfer artifact, pull
requests should update `parser_implementation_reference.md` whenever parser
behavior, parser coverage, parser fixtures/goldens, or parser validation flow
meaningfully changes.

A CI guard in `.github/workflows/tests.yml` enforces this on pull requests by
failing when parser-related files change without a matching update to this
reference. The guard currently watches these path groups:

- `fortran_parser/`
- `tests/fcode/`
- `tests/test_fortran_signature_parser.py`
- `.github/workflows/`

If a specific PR is a legitimate exception, either:

- include a brief no-op/reference update here explaining why no behavior-level
  doc change is needed, or
- adjust the guard patterns in CI to better match actual parser-impacting
  paths.

Manual force mode is also supported: add the pull-request label
`require-parser-reference-update` to require this document update even when the
parser-impact path patterns do not match. With that label present, CI fails
unless `parser_implementation_reference.md` is updated in the PR diff.


### Parser error-raising rules (quick guardrail)

When updating parser behavior, keep this fail-fast contract aligned with tests:

- **Version/source-form mismatch (hard error):**
  - For files detected as Fortran 77 (`.f`, `.for`, `.ftn`, `.f77`), modern-only syntax raises `ValueError` (for example: `::`, `intent(...)`, `module`, `contains`, `interface`, `use`, `class(...)`).
  - For files detected as modern (`.f90`, `.f95`, `.f03`, `.f08`), legacy star-kind declarations (e.g. `real*8`) raise `ValueError`.
- **Unknown datatype declaration (hard error):**
  - Procedure declarations, derived-type fields, and module-variable declarations raise `ValueError` when the datatype declaration is unknown/unsupported instead of silently skipping.
- **Design intent:**
  - The parser is intentionally strict at parse time to avoid mixed-standard inputs producing ambiguous metadata.
  - "Unsupported but recognized" constructs are still surfaced via readiness diagnostics where appropriate; truly invalid-for-version or unknown datatype syntax should crash early.

Implementation note: enforce these checks close to lexical declaration handling (source-form check + declaration parse) so behavior is consistent across signatures, types, modules, and interfaces.
