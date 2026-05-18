# Parser implementation reference (feature inventory)

This is an implementation-level checklist of what this repository already handles,
intended as a transfer document for re-implementing the same architecture for
another source language.

## 1) End-to-end capabilities

- Parse individual Fortran sources into normalized callable signatures.  
- Parse derived types (including inheritance and type-bound procedures).  
- Parse modules (including module `use` imports, renamed import mappings, and
  module variables).
- Parse interfaces and procedures declared inside interfaces.  
- Parse multi-file projects with dependency-aware ordering.  
- Resolve compile-time symbols used in type kinds and array shapes, both local
  and cross-file via imported modules.  
- Produce wrap-readiness diagnostics (`unsupported_constructs`, unknown
  argument declarations, wrappable boolean).  
- Provide CLI output in both human-readable tree form and JSON form.  

## 2) Language coverage actually implemented

### 2.1 Source forms, lexing, and preprocessing

- Free-form Fortran suffixes: `.f90`, `.f95`, `.f03`, `.f08`.  
- Fixed-form suffixes: `.f`, `.for`, `.ftn`, `.f77`.  
- Comment stripping and continuation folding via preprocessing stage.  
- Fortran-77 fixed-form continuation support validated by tests.  
- Source-form suffixes are preprocessing hints, not language-era gates:
  parseable modern constructs are not rejected solely because the filename uses
  a legacy suffix, and parseable legacy constructs are not rejected solely
  because the filename uses a modern suffix.

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
- Procedure-scope `import :: symbol` inside interface bodies is preserved on
  the parsed interface procedure signature as `import(symbol)`.

### 2.3 Types, arguments, declarations

- Intrinsic bases: `integer`, `real`, `complex`, `logical`, `character`,
  and `double precision` (normalized as `real`).  
- Derived argument declarations through `type(<name>)`.  
- Procedure dummy declarations through `procedure(<interface>)`.  
- Legacy star-kind forms are accepted where represented by the declaration
  grammar. Modern declarations such as `real*8 :: x` preserve kind metadata;
  old fixed-form declarations without `::`, such as `real*8 x`, preserve kind
  metadata too.
- Declaration attributes extracted:
  - `intent(in|out|inout)`
  - `optional`
  - `value`
  - `allocatable`
  - `pointer`
- Rank/shape extraction from:
  - declaration-level `dimension(...)`
  - variable-level inline shape `x(...)`
- Structured shape components are available from model helpers while preserving
  serialized `shape` tokens:
  - `shape_info`: per-dimension `{raw, lower, upper}`
  - `lower_bounds` / `upper_bounds` convenience accessors
  - For extent-only forms like `x(n)`, bounds normalize to lower=`1`, upper=`n`
- Typed shape/specification helpers are available without changing serialized
  JSON:
  - `FortranShape` for the full parsed shape
  - `FortranSlice` for `lower:upper[:stride]` dimensions
  - `FortranFunctionCall` for whole-expression calls such as `ubound(x, 1)`
  - `kind_expression` / `value_expression` for non-shape specs
- Builtin kind extraction and assignment into argument/result metadata:
  - positional forms such as `integer(4)`, `real(8)`, `complex(16)`,
    `logical(1)`, and `character(1)`
  - keyword forms such as `integer(kind=c_int)`, `real(kind=rk)`, and
    `complex(kind=c_double_complex)`
  - character length forms such as `character(len=8)` and combined character
    specs such as `character(len=1, kind=c_char)`
  - legacy star-kind forms covered by tests
  Numeric, symbolic, and expression-like kind tokens are preserved when the
  declaration grammar can recognize the surrounding datatype. This is not "any
  datatype"; unknown base datatypes still fail fast as unsupported declarations.

### 2.4 Compile-time symbol and expression resolution

- Local `parameter` constants collected inside procedure scope.  
- Module-scope `parameter` constants collected in module specification part.  
- `use <module>, only: ...` symbol import maps collected and attached to
  procedures/modules. Each explicit import records the imported `source` name
  and optional local `target` name so renamed imports survive JSON,
  semantic conversion, and `.pyi` printing.  
- Signature kind expressions resolved transitively (symbol -> symbol -> value).  
- Shape expressions resolved using available symbol dictionary.  
- Namespace/project parsing resolves cross-file kinds and dimensions after
  dependency ordering.  

### 2.5 Modules

- Module discovery with module context assignment to contained entities.  
- Module-level `use` dependencies parsed (including `only` symbol lists and
  rename forms such as `local => remote`).  
- Module variables extracted from specification part declarations.  
- Module records enriched with child entities:
  - contained procedures
  - contained derived types
  - contained interfaces
- Module-level `use` imports propagated to contained procedures at parse time.  

### 2.6 Derived types

- `type :: name ... end type` and legacy `type name ... end type` discovery.  
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

### 2.8 Submodules and additional program units

- Fortran 2008 `submodule (parent) name` and `submodule (ancestor:parent) name` blocks detected.
- Submodule specification-part `use` statements and variables captured.
- Submodule procedure implementations recognized via `module subroutine/function` and `module procedure`.
- Main `program` and `block data` units are parsed into dedicated model objects.

### 2.9 Wrap-readiness analysis

- Unsupported construct patterns explicitly scanned:
  - assumed-type polymorphic `class(*)`
  - `select type`
  - coarray forms
  - `procedure, pointer`
  - `type(c_ptr)`
- Unknown argument declaration tracking (`base_type == "unknown"`).  
- Summary report fields:
  - `n_signatures`, `n_types`, `n_modules`, `n_submodules`, `n_programs`, `n_block_data`
  - `unsupported_constructs`
  - `unknown_argument_types`
  - `wrappable`

## 3) Output/data model behavior

- Core parsing APIs return typed model objects (procedures, arguments, modules,
  submodules, programs, block data, types, interfaces, variables).
- `FortranUseMapping(source, target)` represents explicit `use` symbols.
  `source` is the imported provider-side symbol. `target` is the local name
  for renamed imports, or `None` when the local name is the same as `source`.
  `local_name` returns `target or source`.
- `FortranShape`, `FortranSlice`, and `FortranFunctionCall` provide typed
  views over argument/variable specification strings. They are exposed through
  properties, so existing parser JSON remains stable.
- Namespace parse returns aggregate dictionary with:
  - ordered file list
  - file dependency graph
  - module-to-file and submodule-to-file indexes
  - merged modules/submodules/programs/block-data/types/signatures
- CLI JSON output emits per-file buckets for signatures, types, modules,
  readiness report.  
- CLI human output prints tree-like structure grouped by file/module/procedure.  
- Parser JSON serializes explicit `use` symbols as objects containing
  `source` and `target`. Bare imports still use an empty list.
- Semantic IR imports use structured `SemanticImport` / `SemanticImportItem`
  entries when a Fortran `use` has an explicit symbol list; bare imports remain
  plain module names for compatibility.
- The `.pyi` printer emits structured imports as `from module import name` or
  `from module import source as target`; the `.pyi` parser accepts the same
  syntax and restores the semantic import mapping.

## 4) Test strategy implemented (current workflow)

### 4.1 Day-to-day test command

Primary regression command:

- `python -m pytest -q`

This runs the full parser test suite, including fixtures, corpus checks, CLI,
and error handling coverage.

### 4.2 Unit-style parser tests (`tests/parser/test_*.py`)

Covers, among others:
- `tests/parser/test_procedure_and_type_parsing.py`
- `tests/parser/test_scope_handling.py`
- `tests/parser/test_error_handling.py`
- `tests/parser/test_parser_public_api_coverage.py`
- intent/kind/rank extraction for routine arguments
- function result parsing + `use` extraction
- `use` rename preservation, intrinsic/non-intrinsic import forms, and parser
  public API coverage for less common constructs
- fixed-form parsing and interface detection
- cross-file kind resolution from imported module parameters
- derived type fields and method detection
- storage directives (`save`, `common`) in procedures are recognized and skipped as non-declaration statements
- module variable and `use` parsing
- module children attachment (procedures/types/interfaces)
- ignoring local vars in external signatures
- external callback declarations (including typed `real, external :: f`) under `implicit none`
- ignoring internal procedures in `contains`
- local parameter propagation into argument kinds
- compile-time shape expression evaluation helpers
- shape symbol collection helpers
- readiness diagnostics and unsupported detection

### 4.3 Fixture and corpus regression (`tests/parser/test_fortran_fixture_suite.py`)

- Golden fixture tests:
  - parse shared Fortran fixtures under `tests/data/fortran/general`
  - compare normalized parse output against parser JSON goldens under
    `tests/parser/fortran/fixtures/general`
- Large corpus parse-only sanity tests:
  - parse BLAS source fixtures under `tests/data/fortran/blas`
  - parse LAPACK source fixtures under `tests/data/fortran/lapack`
  - parse SciFortran source fixtures under `tests/data/fortran/scifortran`
    against direct parser goldens under `tests/parser/fortran/fixtures/scifortran`

The corpus checks provide broad “does it parse?” coverage over many real-world
fixed/free-form Fortran files without requiring full golden outputs for each.
Several real-world corpus files also have direct parser goldens. When parser
JSON schema changes, those fixtures should be regenerated so broad coverage
continues to validate the serialized model shape.

### 4.4 Golden regeneration support

- Script provided: `tests/parser/fortran/generate_fortran_parser_goldens.py`.
- Use when parser behavior is intentionally changed and golden JSON needs
  updating.
- Optional in-test auto-update flow is also supported:
  - `FORTRAN_PARSER_UPDATE_GOLDENS=1 python -m pytest -q tests/parser/test_fortran_fixture_suite.py --confcutdir=tests/`
- Semantic and `.pyi` fixture generators are separate:
  - `python tests/semantics/generate_semantic_fixtures.py`
  - `python tests/pyi/generate_pyi_fixtures.py`

### 4.5 CLI tests (`tests/parser/test_cli.py`)

Validates command-line behavior for:
- path expansion
- human-readable output
- JSON output
- JSON file writing
- module/free-procedure name collision handling
- parse-error diagnostics without tracebacks by default
- developer traceback opt-in through `--debug-traceback` and `FORTRAN_PARSER_DEBUG=1`
- default ANSI color for diagnostics, with `--no-color` and `NO_COLOR=1` opt-out

### 4.6 Error handling tests (`tests/parser/test_error_handling.py`)

Dedicated tests for the error handling system:
- `FortranParseError` attribute presence (`filename`, `line_number`, `source_line`, `base_message`, `code`)
- Compiler-style diagnostic formatting with `PARSE001`, source line context, and caret marker
- ANSI color formatting and environment-variable debug activation
- Error raised for all error categories in all scopes: procedures, modules, derived types, interfaces
- Line number accuracy
- `FortranParseError` is a subclass of `ValueError` (backward compatibility)

## 5) Repository/file structure reference

- `fortran_parser/lexer.py`
  - line preprocessing, source-form handling, continuation/comment normalization; returns tuples of `(preprocessed_line, original_line_number, original_source_line)` for downstream error reporting.
- `fortran_parser/parser.py`
  - main grammar subset parser and orchestration functions.
- `fortran_parser/type_resolver.py`
  - kind extraction and symbol/expression helpers.
- `fortran_parser/models.py`
  - parser data structures / model schema; includes `FortranParseError` and its compiler-style diagnostic renderer.
- `fortran_parser/utils.py`
  - shared text utilities (e.g., CSV-like splitting used by declarations).
- `fortran_parser/cli.py`
  - CLI argument parsing, report formatting, and user-facing parse-error handling.
- `fortran_parser/__main__.py`
  - `python -m x2py` entry point.
- `tests/parser/test_*.py`
  - focused behavior tests per feature.
- `tests/parser/test_error_handling.py`
  - dedicated error handling and `FortranParseError` behavior tests.
- `tests/parser/test_fortran_fixture_suite.py`
  - fixture-vs-golden regression checks.
- `tests/parser/test_parser_public_api_coverage.py`
  - targeted coverage for parser public API behavior that is easy to miss in
    fixture-only tests.
- `tests/parser/test_cli.py`
  - end-user command behavior tests.
- `tests/data/fortran/`
  - shared Fortran fixture corpus used by parser, semantics, and pyi tests.
- `tests/parser/fortran/fixtures/`
  - parser golden parse outputs.
- `tests/parser/fortran/generate_fortran_parser_goldens.py`
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
  Interface-local argument declarations do not conflict with host declarations;
  callback dummies referenced by interface headers are typed as `procedure`.
- **Interface import tracking**: `import :: symbol` inside an interface
  procedure is treated as procedure metadata and emitted as an `import(symbol)`
  signature attribute, rather than as a module variable declaration.
- **Internal procedure scope protection**: nested procedures in a host
  `contains` block are not merged into the host routine signature.
- **Name-reuse safety across scopes**: fixtures/tests cover same identifier
  reuse in separate host/internal/type scopes to ensure no cross-scope symbol
  pollution.
- **Preprocessor branch-aware duplicate checks**: duplicate procedure names are
  allowed in mutually exclusive `#if/#ifdef` branches but still raise when two
  same-name procedures are active in overlapping branch conditions.
- **Valued variables map**: compile-time constants are preserved as
  `FortranVariable(name, value)` records in signature metadata.
- **Expression normalization using valued variables**: argument kinds and shape
  expressions are rewritten using the resolved valued-variable map, including
  transitively dependent symbols.
- **Imported constant merge policy**: local/module/imported constants are merged
  into a single symbol-value dictionary with precedence that preserves explicit
  procedure-local definitions.
- **Use rename mapping policy**: explicit `use` imports are represented as
  source/target pairs. A missing target means the local name equals the source;
  renamed imports preserve both names for downstream semantic IR and `.pyi`
  `import as` emission.

## 8) Implementation timeline highlights from repository history

A condensed history of important parser capabilities added over time (from
`git log`):

- Improved argument declaration parsing plus shape/derived coverage.
- Added assumed-shape bounds and derived-argument fixture coverage.
- Added compile-time shape-expression resolution from parameters.
- Added symbolic shape-evaluation API for externally supplied symbol values.
- Added structured per-dimension shape component helpers (`raw/lower/upper`).
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
- Added parser public API coverage for less common module/import forms and
  preserved `use` rename source/target mappings through JSON, semantic IR, and
  `.pyi` import aliases.

## 9) Pull-request maintenance policy for this reference

To keep this document useful as an implementation transfer artifact, pull
requests should update `parser_implementation_reference.md` whenever parser
behavior, parser coverage, parser fixtures/goldens, or parser validation flow
meaningfully changes.

A CI guard in `.github/workflows/tests.yml` enforces this on pull requests by
failing when parser-related files change without a matching update to this
reference. The guard currently watches these path groups:

- `fortran_parser/`
- `tests/parser/`
- `tests/data/fortran/`

If a specific PR is a legitimate exception, either:

- include a brief no-op/reference update here explaining why no behavior-level
  doc change is needed, or
- adjust the guard patterns in CI to better match actual parser-impacting
  paths.

Manual force mode is also supported: add the pull-request label
`require-parser-reference-update` to require this document update even when the
parser-impact path patterns do not match. With that label present, CI fails
unless `parser_implementation_reference.md` is updated in the PR diff.

Manual ignore mode is supported: add the pull-request label
`ignore-parser-reference-guard` to skip the parser reference guard entirely.
Use this sparingly (e.g. doc-only refactors, purely mechanical changes) to avoid
the reference drifting from actual parser behavior.


### Parser error-raising rules (quick guardrail)

When updating parser behavior, keep this fail-fast contract aligned with tests:

- **Source-form is not a language-era hard gate:**
  - Filename suffixes choose preprocessing behavior and compatibility metadata.
    Fixed-form suffixes (`.f`, `.for`, `.ftn`, `.f77`) use fixed-form
    continuation/comment handling; modern suffixes (`.f90`, `.f95`, `.f03`,
    `.f08`) use free-form handling.
  - The parser does not reject mixed-era constructs solely because of suffix.
    For example, `module`/`interface` syntax in a `.f77` file is parsed if the
    fixed-form preprocessor produces valid logical lines, and legacy star-kind
    syntax in `.f90` is parsed when the declaration grammar recognizes it.
  - Wrapper generation/readiness should decide whether a parsed feature is safe
    to wrap. Parser errors should be about unsupported grammar/metadata, not
    about a filename implying an older or newer language standard.
- **Unknown datatype declaration (hard error):**
  - Procedure declarations, derived-type fields, and module-variable declarations raise `FortranParseError` when the datatype declaration is unknown/unsupported instead of silently skipping.
- **Datatype and kind support is bounded by the declaration grammar:**
  - Supported base declaration families include intrinsic scalar bases,
    `type(...)`/`class(...)` derived types, and `procedure(...)` dummy
    procedure declarations.
  - Supported kind forms include parenthesized positional specs, `kind=...`,
    character `len=...` specs, combined character length/kind specs, legacy
    star-kind forms covered by tests, and symbolic/expression tokens that can
    later be resolved from local or imported parameters.
  - Unresolved but syntactically valid kind symbols are not parser errors by
    themselves; wrap-readiness reports them as `unresolved_kind_arguments` or
    `unresolved_kind_fields` when they cannot be found in the parsed source or
    imports.
- **Post-scope validation (hard error):**
  - After parsing each module, derived type, or procedure scope, a validation pass checks that all declared variables/fields/arguments have a known (non-`"unknown"`) base type; failures raise `FortranParseError`.
  - Under `implicit none`, missing declarations are treated as hard errors. For functions:
    - if the header uses an explicit `result(name)`, an undeclared result raises an "Unknown datatype for function result ..." error for that result symbol
    - otherwise the result is implicitly the function name and the usual "has no type declaration (implicit none is active)" wording is used
- **Design intent:**
  - The parser is intentionally strict about unknown declarations and internal
    metadata consistency, but permissive about mixed-era Fortran syntax that can
    be parsed unambiguously.
  - "Unsupported but recognized" constructs are still surfaced via readiness
    diagnostics where appropriate; unknown datatype syntax should crash early.
- **Preprocessor-conditional duplicate procedures (guarded allowance):**
  - The parser does **not** run a full C preprocessor stage before parsing.
  - While scanning signatures, simple directive structure is tracked for `#ifdef`, `#ifndef`, `#elif`, `#else`, and `#endif` to model mutually-exclusive branches.
  - `visit_fortran_file(..., macro_defines=...)` can provide macro decisions; inactive conditional branches are skipped during signature extraction so the active code path is selected. The legacy `parse_fortran_file(...)` alias remains for compatibility.
    - accepted forms: `set[str]` or `dict[str, int|bool|str]`
    - dictionary values are truthy/falsey (`0`, `False`, `"0"`, `"false"` treated as undefined/disabled)
  - Basic `#if` expressions are supported for branch selection (`defined(X)`, `!`, `&&`, `||`, parentheses, `0`/`1`).
  - Duplicate procedure-name checks in a module/global scope are evaluated against this branch context:
    - if two same-name procedure headers are reachable in an overlapping branch context, raise `FortranParseError` (duplicate procedure name).
    - if they are only present in mutually-exclusive branches of the same conditional group, allow both signatures.
  - This is a structural exclusivity model (branch groups), not semantic evaluation of macro expressions. In other words, branch mutual exclusivity is honored without requiring expression truth evaluation.

`FortranParseError` is a subclass of `ValueError` and carries structured location metadata:
- `filename` — source file path (if provided)
- `line_number` — 1-based line number in the original source where the error was detected
- `source_line` — the original (pre-preprocessed) source line text
- `base_message` — the stable error message without source/location context
- `code` — diagnostic code; current parser errors default to `PARSE001`
- `parser_file`, `parser_line_number`, `parser_function` — internal raise-site metadata used only for debug diagnostics

The formatted `str()` of `FortranParseError` is a compiler-style diagnostic:

```text
<filename>:<line>:1: error[PARSE001]: <base_message>
  |
<N> | <source_line>
  | ^
```

Use `error.format_diagnostic(color=True)` to add ANSI color and
`error.format_diagnostic(debug=True)` to append a `note: parser raised at ...`
line with the internal parser location. `format_diagnostic(debug=None)` also
honors `FORTRAN_PARSER_DEBUG=1`.

CLI contract:
- End-user parse failures are caught, rendered to `stderr` with
  `format_diagnostic(...)`, and return exit status `1`; they do not print Python
  tracebacks by default.
- CLI diagnostics request ANSI color by default when available.
- `--no-color` and `NO_COLOR=1` disable ANSI color in CLI diagnostics.
- `--debug-traceback` re-raises `FortranParseError` so Python prints the full
  traceback for parser developers.
- `FORTRAN_PARSER_DEBUG=1` enables the same traceback/debug behavior without
  changing command-line arguments.

Implementation note: enforce these checks close to lexical declaration handling (source-form check + declaration parse) so behavior is consistent across signatures, types, modules, and interfaces. Preserve the original source line and line number whenever possible so diagnostics can show the Fortran source context rather than only the error text.
