# C Parser Implementation Checklist

Status: implementation checklist with Phase 1 skeleton, selected Phase 2
fixture scaffolding, selected Phase 3 model/error work, Phase 4 raw
lexer/directive metadata, and a first Phase 5/6 partial
declaration/function subset complete. The `c_parser` package and explicit C
parse path exist, and simple variables, typedefs, function prototypes,
function-definition signatures, function-definition start/end locations, and
incomplete `struct`/`union` declarations and basic aggregate definitions are
now parsed. Declarators use a recursive grammar-style parser for pointer,
array, function, and parenthesized combinations. Declaration types are concrete
`CType` subclasses combined by `CComposedType`; aggregate members are
`CVariable` objects using the same declared-type path. Selected unsupported
extensions are diagnosed, and invalid primitive-specifier combinations raise
`CParseError` without treating unresolved single typedef-name uses as invalid.
Aggregate members carry their own source locations, and flexible array
members are classified and checked for supported struct/union constraints.

This checklist is intentionally detailed so future work can proceed one branch,
one checklist item, and one tested capability at a time. The C parser initiative
must remain isolated from project `main` until the frontend is mature and
stable.

## Progress Snapshot

- Last updated: 2026-05-24
- Checklist progress: 516/848 checked (60.8%).
- Current parser status: partial C parser with raw directive metadata, top-level
  source splitting, simple declarations/variables/typedefs, prototype-style
  metadata, K&R diagnostics, simple function signatures, and start/end
  locations for function definitions. Incomplete struct/union declarations are
  recorded as `CStruct`/`CUnion` values with `is_incomplete=True`; named tags
  are indexed at project level. Parenthesized declarators, function pointer
  typedefs/parameters, callback members, and functions returning function
  pointers are represented with concrete `CType` objects and
  `CComposedType.components`. Primitive specifiers have concrete type classes,
  valid spelling permutations are normalized, invalid combinations raise
  `CPARSE003`, and functions, variables, typedefs, and aggregates are
  distinguished by their concrete declaration objects rather than a kind field.
  Struct and union fields now preserve per-member locations; legal final
  flexible struct members are marked through `CArray.is_flexible`, with error
  diagnostics for invalid placement or union use.

## Global Rules

- [ ] Keep all C parser work on `c-parser/main` and child branches until the
      frontend is stable.
- [ ] Do not merge C parser work directly into project `main`.
- [ ] Keep the Fortran parser behavior unchanged unless a future task
      explicitly requires shared infrastructure changes.
- [x] Put C parser implementation in a separate `c_parser` package.
- [x] Keep C parser tests separated from existing Fortran tests.
- [x] Gate all integration through explicit C flags or C-specific APIs.
- [ ] Keep any C wrappability assessment in the semantic layer, not inside the
      parser package.
- [x] Implement C parsing as a grammar-style recursive parser with scoped
      visitors, source slicing, shared declaration/declarator parsing helpers,
      and typed model objects.
- [x] Store initial C-specific facts in `c_parser/models.py`; defer semantic IR
      extensions until the C parser models prove what information is needed.
- [ ] Keep the C parser main-merge guard active for C parser branches and
      paths.
- [ ] Require the `c-parser-ready-for-main` label only for the final approved
      merge into project `main`.
- [x] Do not implement a giant regex parser.
- [x] Do not implement a whole-file scanner as the core architecture.
- [x] Do not make libclang the only parser architecture.
- [ ] Do not make compiler preprocessing a replacement for x2py parser models,
      source locations, diagnostics, or project indexes.
- [x] Preserve the semantic IR layer as the source of truth.
- [x] Treat documentation as a first-class deliverable in every phase.
- [ ] Whenever C parser behavior, models, CLI behavior, tests, fixture
      workflows, semantic integration, or `.pyi` behavior change, update every
      affected file under `docs/c_parser/` in the same change. Do not wait for
      a separate documentation request.
- [x] Update this checklist when implementation reality changes.

## Phase 0: Repository Inspection, Branch Setup, And Roadmap

Branch target:

- `c-parser/main`
- `c-parser/phase-0-roadmap`

Scope:

- Planning only.
- Documentation only.
- No parser package.
- No parser logic.
- No CLI code changes.
- No fixture generation.

### Branch And Isolation Tasks

- [x] Start from project `main`.
- [x] Create long-lived integration branch `c-parser/main`.
- [x] Create planning branch `c-parser/phase-0-roadmap` from
      `c-parser/main`.
- [x] Merge `c-parser/phase-0-roadmap` back into `c-parser/main`.
- [x] Confirm `main` has no C parser planning commits unless intentionally
      merged later after stabilization.
- [x] Record the branch strategy in C parser docs.
- [x] Use `codex: ...` prefix for planning commit message.

### Repository Inspection Tasks

- [x] Inspect `README.md`.
- [x] Inspect `fortran_parser.md`.
- [x] Inspect `parser_implementation_reference.md`.
- [x] Inspect `Semantic_Multilanguage_Wrapper_Runtime_Architecture.md`.
- [x] Inspect `docs/pyi_format.md`.
- [x] Inspect `fortran_parser/lexer.py`.
- [x] Inspect `fortran_parser/parser.py`.
- [x] Inspect `fortran_parser/models.py`.
- [x] Inspect `fortran_parser/type_resolver.py`.
- [x] Inspect `fortran_parser/utils.py`.
- [x] Inspect `fortran_parser/cli.py`.
- [x] Inspect `x2py/cli.py`.
- [x] Inspect `x2py/__init__.py`.
- [x] Inspect `semantics/models.py`.
- [x] Inspect `semantics/fortran2ir.py`.
- [x] Inspect `semantics/pyi_printer.py`.
- [x] Inspect `semantics/pyi_parser.py`.
- [x] Inspect parser CLI tests.
- [x] Inspect parser public entrypoint tests.
- [x] Inspect parser developer tutorial tests.
- [x] Inspect semantic wrap-readiness tests.
- [x] Inspect parser error handling tests.
- [x] Inspect parser fixture/golden suite.
- [x] Inspect parser golden regeneration script.
- [x] Inspect parser error golden regeneration script.
- [x] Inspect semantic conversion tests.
- [x] Inspect semantic fixture generator.
- [x] Inspect `.pyi` tests.
- [x] Inspect `.pyi` fixture generator.
- [x] Avoid spending analysis on ignored Fortran source fixtures except file
      layout and fixture workflow.
- [x] Avoid spending analysis on generated JSON fixtures.

### Planning Document Tasks

- [x] Create `docs/c_parser/`.
- [x] Create `docs/c_parser/c_parser_reference.md`.
- [x] Create `docs/c_parser/c_parser_architecture.md`.
- [x] Create `docs/c_parser/c_parser_cli_workflow.md`.
- [x] Create `docs/c_parser/c_parser_implementation_checklist.md`.
- [x] Create `docs/c_parser/c_parser_main_merge_guard.md`.
- [x] Document the branch isolation strategy.
- [x] Document the main-merge guard policy.
- [x] Document Fortran parser architecture observations.
- [x] Document proposed C parser package layout.
- [x] Document public API shape.
- [x] Document CLI command shape.
- [x] Document early skeleton CLI behavior.
- [x] Document JSON schema direction.
- [x] Document semantic readiness direction.
- [x] Document semantic IR mapping direction.
- [x] Document `.pyi` integration direction.
- [x] Document v1 non-goals.

### Phase 0 Definition Of Done

- [x] Planning docs exist under `docs/c_parser/`.
- [x] Docs clearly say no parser implementation exists yet.
- [x] Docs make CLI and documentation Phase 1 deliverables.
- [x] Docs preserve the grammar-style parser requirement.
- [x] Docs preserve project-main isolation.
- [x] Main-merge guard policy is documented.
- [x] Planning branch is committed.
- [x] Planning branch is merged into `c-parser/main`.

### Phase 0 Test Expectations

- [x] No test changes are required in Phase 0.
- [x] Run a documentation-safe sanity command such as `git status`.
- [x] Do not regenerate fixtures.
- [x] Do not run parser golden update scripts.

### Phase 0 Risks And Open Questions

- [x] Decide whether the future package should be named `c_parser` or another
      name before code lands.
- [x] Decide whether `x2py.__init__` should expose C APIs during skeleton phase
      or wait until Phase 3 models are useful.
- [x] Decide whether C debug env var should be `C_PARSER_DEBUG` or generic
      `X2PY_DEBUG`.

## Phase 1: CLI And Documentation Skeleton First

Branch target:

- `c-parser/phase-1-cli-and-docs`

Scope:

- User-visible command shape.
- Documentation skeleton.
- Placeholder C parser reports.
- CLI tests.
- No real parser logic.

### Documentation Tasks

- [x] Update `docs/c_parser/c_parser_cli_workflow.md` with implemented command
      examples.
- [x] Update `docs/c_parser/c_parser_reference.md` with skeleton CLI behavior.
- [x] Add a "Current Status" section showing which C features are placeholder
      only.
- [x] Document how C parser output differs from Fortran parser output.
- [x] Document that auto-detection is deferred.
- [x] Document that `--language c` is required initially.
- [x] Document unsupported `--semantics --language c` behavior.
- [x] Document unsupported `--pyi --language c` behavior.
- [x] Document C parser diagnostics even if only skeleton diagnostics exist.
- [x] Add examples for parse tree, JSON, and output file behavior.

### CLI Design Tasks

- [x] Add `--language {fortran,c}` to `x2py.cli`.
- [x] Preserve current Fortran behavior when `--language` is omitted.
- [x] Make `--language fortran` equivalent to current behavior.
- [x] Add explicit C parse path behind `--language c --parse`.
- [x] Decide not to add `--parse-c` alias in this phase.
- [ ] If `--parse-c` is added, make it an alias for `--language c --parse`.
- [x] Reject `--language c` without a supported stage flag.
- [x] Reject `--language c --semantics` until Phase 10.
- [x] Reject `--language c --pyi` until Phase 11.
- [x] Reject Fortran-only flags in C mode if they do not apply.
- [x] Keep `--json` behavior stable for parse output.
- [x] Keep `--out` behavior stable for C parse JSON.
- [x] Keep `--no-color` accepted in C mode.
- [x] Keep `--debug-traceback` accepted in C mode.
- [x] Do not change `fortran_parser.cli` unless a compatibility reason is
      documented.

### Skeleton Report Tasks

- [x] Create a minimal C report provider without real parsing.
- [x] Ensure skeleton C report can accept `.c` and `.h` paths.
- [x] Ensure skeleton C report can accept directories only in explicit C mode.
- [x] Return `language: "c"` in C JSON output.
- [x] Return `parser_status: "skeleton"` in C JSON output.
- [x] Return empty `functions` list.
- [x] Return empty `structs` list.
- [x] Return empty `unions` list.
- [x] Return empty `enums` list.
- [x] Return empty `typedefs` list.
- [x] Return empty `variables` list.
- [x] Return `macros` list, empty until raw macro directives are found.
- [x] Return `includes` list, empty until raw include directives are found.
- [x] Return `diagnostics` list, empty unless skeleton or raw metadata
      diagnostics are found.
- [x] Human tree output should show zero-count C sections and skeleton status.

### CLI Test Tasks

- [x] Add C CLI tests in a C-specific test file, for example
      `tests/parser/test_c_cli_skeleton.py` or `tests/c_parser/test_cli.py`.
- [x] Test existing Fortran CLI behavior still passes.
- [x] Test `--help` shows `--language`.
- [x] Test `--language c --parse` accepts a temporary `.h` file.
- [x] Test `--language c --parse --json` emits valid JSON.
- [x] Test `--language c --parse --out report.json` writes JSON and suppresses
      stdout.
- [x] Test `--language c --semantics` returns argparse error or clear
      unsupported-stage error.
- [x] Test `--language c --pyi` returns argparse error or clear
      unsupported-stage error.
- [x] Test `--language c --parse --show-vars` is rejected or ignored with
      documented behavior.
- [x] Test `--parse` without `--language` remains Fortran behavior.
- [ ] If `--parse-c` is added, test it maps to C parse mode.
- [x] Test `--no-color` is accepted in C mode.
- [x] Test `NO_COLOR=1` is honored once C diagnostics exist.
- [x] Test `--debug-traceback` is accepted in C mode.

### Phase 1 Definition Of Done

- [x] Users can discover C mode from CLI help.
- [x] Users can run a stable C parse skeleton command.
- [x] C JSON skeleton output has a documented schema.
- [x] Fortran CLI behavior is unchanged.
- [x] Documentation includes the exact command workflow.
- [x] Tests cover the skeleton command workflow.

### Phase 1 Risks And Open Questions

- [x] Decide whether to implement a temporary skeleton module inside
      `x2py.cli` or create `c_parser/cli.py` early.
- [x] Decide whether skeleton output should include zero-count sections in
      human output or omit empty sections like Fortran.
- [x] Decide whether `--json` should eventually support semantic C output or
      stay parse-only.

## Phase 2: Testing Infrastructure

Branch target:

- `c-parser/phase-2-testing`

Scope:

- Test directories, fixtures, golden scripts, and update workflow.
- Minimal placeholder fixtures are allowed.
- Skipped roadmap tests are allowed before parser implementation exists.
- No real parser logic unless needed to support skeleton output already added.

### Test Layout Tasks

- [x] Create a dedicated C parser test area.
- [x] Choose between `tests/c_parser/` and `tests/parser/c/` for focused C
      parser tests.
- [x] Create `tests/data/c/general/`.
- [x] Create `tests/data/c/errors/parser/`.
- [x] Create `tests/data/c/corpus/`.
- [x] Create `tests/data/c/scientific/`.
- [ ] Create `tests/parser/c/fixtures/general/`.
- [ ] Create `tests/parser/c/fixtures/errors/`.
- [x] Keep C fixture data separate from Fortran fixture data.
- [x] Add README files explaining each C fixture directory.
- [x] Add small `.h` and `.c` fixture files for C fixture coverage.

### Skipped Roadmap Test Policy

- [x] Add skipped C parser roadmap tests before implementation starts.
- [x] Keep every roadmap test skipped until its implementation branch lands.
- [x] Keep `c_parser` imports inside skipped test functions, not at module
      import time, so collection works before the package exists.
- [x] Use the skipped tests as an executable checklist for future branches.
- [x] Unskip tests one capability at a time.
- [x] In each implementation branch, unskip only the tests covered by that
      branch.
- [x] Do not unskip broad fixture, corpus, semantic, or `.pyi` tests before
      the supporting workflow exists.
- [x] When a skipped test is unblocked, replace placeholder expectations with
      the exact implemented model fields if the final schema differs.
- [x] Keep the skipped C suite separate from existing Fortran tests.
- [ ] Keep Fortran tests green whenever C tests are unskipped.

### Skipped Roadmap Test Files

- [x] Create `tests/parser/c/README.md` with the staged unskip policy.
- [x] Create `tests/parser/c/test_c_public_entrypoints.py`.
- [x] Create `tests/parser/c/test_c_cli.py`.
- [x] Create `tests/parser/c/test_c_lexer_preprocessor.py`.
- [x] Create `tests/parser/c/test_c_declarations_and_declarators.py`.
- [x] Create `tests/parser/c/test_c_functions.py`.
- [x] Create `tests/parser/c/test_c_structs_unions_enums_typedefs.py`.
- [x] Create `tests/parser/c/test_c_project_includes.py`.
- [x] Create `tests/semantics/test_c_semantic_readiness.py` or equivalent
      semantic-layer coverage for C wrappability once that layer exists.
- [x] Create `tests/parser/c/test_c_fixture_suite.py`.
- [x] Create `tests/parser/c/test_c_error_fixture_suite.py`.
- [x] Create `tests/parser/c/test_c_json_sanity.py`.
- [x] Create `tests/parser/c/test_c_corpus.py`.

### Golden Workflow Tasks

- [ ] Create `tests/parser/c/generate_c_parser_goldens.py`.
- [ ] Mirror the Fortran parser golden generator structure.
- [ ] Serialize only dataclass/JSON-stable C parse models.
- [ ] Strip parent/back-reference fields if future models need them.
- [ ] Support updating all fixtures.
- [ ] Support updating selected fixtures.
- [ ] Add an environment variable update flow, for example
      `C_PARSER_UPDATE_GOLDENS=1`.
- [ ] Document whether C uses `C_PARSER_UPDATE_GOLDENS` or a generic
      `X2PY_UPDATE_GOLDENS`.
- [ ] Create a C error golden generator.
- [ ] Store expected error type, message fragments, diagnostic fragments, and
      parser entrypoint metadata.

### Focused Test Buckets

- [x] Add lexer test file.
- [x] Add preprocessor test file.
- [x] Add declaration-specifier test file.
- [x] Add declarator test file.
- [x] Add function parser test file.
- [x] Add struct/union/enum parser test file.
- [x] Add typedef parser test file.
- [x] Add macro/constant parser test file.
- [x] Add project/include parser test file.
- [x] Add semantic readiness test file when C semantic conversion exists.
- [x] Add public entrypoint test file.
- [ ] Add developer tutorial test file once internal helpers exist.
- [x] Add CLI test file.
- [x] Add fixture/golden test file.
- [x] Add error fixture/golden test file.
- [ ] Add semantic conversion tests in Phase 10.
- [ ] Add `.pyi` tests in Phase 11.

### Phase 2 Definition Of Done

- [x] C test directory structure is present.
- [x] C fixture directory structure is present.
- [ ] C golden update workflow is documented.
- [x] Partial parser and metadata tests pass against current behavior.
- [ ] Fortran tests still pass.
- [x] No real parser claims are made without tests.

### Phase 2 Test Expectations

- [x] Run the skipped C roadmap suite and confirm it collects without importing
      `c_parser` at module import time.
- [x] Run C skeleton CLI tests.
- [x] Run existing parser CLI tests.
- [x] Run a small targeted test command, for example
      `python -m pytest -q tests/parser/test_cli.py tests/parser/test_c_cli_skeleton.py`.
- [x] Do not update Fortran goldens.

### Phase 2 Risks And Open Questions

- [x] Decide how much C fixture data is appropriate before parser behavior
      exists.
- [x] Decide whether C parser tests should live alongside Fortran parser tests
      or under a new top-level C test package.

## Phase 3: Parser Package Skeleton, Models, And Serialization Contracts

Branch target:

- `c-parser/phase-3-models`

Scope:

- Create the `c_parser` package.
- Define typed models.
- Define serialization helper contracts.
- Keep actual grammar parsing minimal or placeholder.

### Package Skeleton Tasks

- [x] Create `c_parser/__init__.py`.
- [x] Create `c_parser/__main__.py`.
- [x] Create `c_parser/models.py`.
- [x] Create `c_parser/parser.py`.
- [x] Create `c_parser/lexer.py`.
- [x] Create `c_parser/preprocessor.py`.
- [x] Create `c_parser/type_resolver.py`.
- [x] Create `c_parser/project.py`.
- [x] Create `c_parser/cli.py`.
- [x] Create `c_parser/utils.py`.
- [x] Add `c_parser*` to package discovery in `pyproject.toml`.
- [x] Add `c_parser` to coverage source when implementation begins.
- [x] Keep imports from `x2py.cli` explicit and isolated.
- [x] Keep parser orchestration and helper internals on `CParser`, matching the
      Fortran parser class structure.
- [ ] Split `CParser` internals into smaller visitor/helper classes only if the
      class grows past what remains readable.

### Error Model Tasks

- [x] Implement `CParseError` as a `ValueError` subclass.
- [x] Include `filename`.
- [x] Include `line_number`.
- [x] Include `column`.
- [x] Include `source_line`.
- [x] Include `base_message`.
- [x] Include `code`.
- [x] Include parser raise location for debug diagnostics.
- [x] Implement `format_diagnostic(color=False, debug=None)`.
- [x] Use C diagnostic code prefix such as `CPARSE001`.
- [x] Add color handling equivalent to `FortranParseError`.
- [x] Add optional C debug env var.
- [x] Test C parse error attributes.
- [x] Test compiler-style diagnostic rendering.
- [x] Test color and no-color behavior.
- [x] Test debug note behavior.

### Model Tasks

- [x] Define `CSourceLocation`.
- [x] Define `CDiagnostic`.
- [x] Define concrete `CType` subclasses, including all supported primitive
      scalar and complex types.
- [x] Define `CQualifier` objects (`CConst`, `CVolatile`, `CRestrict`, and
      `CAtomic`).
- [x] Define `CPointer`, `CArray`, `CFunctionType`, and `CComposedType`.
- [x] Define `CParameter`.
- [x] Define `CFunction`.
- [x] Use `CVariable` for struct and union members rather than a separate
      field object.
- [x] Define `CStruct`.
- [x] Define `CUnion` or use `CStruct(is_union=True)`.
- [x] Define `CEnum`.
- [x] Define `CEnumerator`.
- [x] Define `CTypedef`.
- [x] Define `CVariable`.
- [x] Define `CMacro`.
- [x] Define `CInclude`.
- [x] Define `CFile`.
- [x] Define `CProject`.
- [x] Add helper properties for pointer depth.
- [x] Add helper properties for array rank.
- [x] Preserve effective declaration type source text.
- [x] Store qualifiers on the exact `CType` component they qualify.
- [x] Record incomplete aggregate tags with `is_incomplete=True`.
- [x] Add helper properties for source-location display.

### Serialization Tasks

- [x] Add `_to_dict` or equivalent serialization helper.
- [x] Avoid cycles in JSON.
- [x] Keep source locations JSON-serializable.
- [x] Decide whether sets serialize as sorted lists.
- [x] Ensure dataclass defaults produce stable JSON.
- [x] Add tests for empty `CFile` serialization.
- [ ] Add tests for each model's minimal JSON shape.
- [x] Add tests for source-location serialization.
- [ ] Add tests that unknown/unresolved metadata is preserved.

### Public API Skeleton And Partial Parser Tasks

- [x] Implement `CParser` class.
- [x] Implement `CParser.visit_file` returning partial parser `CFile` models.
- [x] Implement `CParser.visit_project` returning partial parser `CProject`
      models.
- [x] Implement module-level `_DEFAULT_PARSER`.
- [x] Implement `parse_c_file`.
- [x] Implement `parse_c_project`.
- [x] Add public API tests for source strings.
- [x] Add public API tests for file paths.
- [x] Add public API tests for empty source.
- [x] Add public API tests for unknown suffix.
- [x] Change parser status from `skeleton` to `partial` once real declaration
      and function facts are populated.
- [x] Add tests that public API output contains parsed functions and project
      indexes for the supported subset.

### Phase 3 Definition Of Done

- [x] `c_parser` imports cleanly.
- [x] Partial public APIs return typed models.
- [x] JSON serialization is stable and tested.
- [x] C CLI uses `c_parser` rather than a temporary inline provider.
- [x] Fortran parser API remains unchanged.
- [x] Docs describe the new package and API status.

### Phase 3 Risks And Open Questions

- [x] Decide whether `CUnion` should subclass/share `CStruct`.
- [x] Decide how to represent anonymous structs/unions/enums.
- [ ] Decide whether macros belong in `CFile.macros` only or also symbols.
- [x] Decide on concrete `CType` objects and name-outward
      `CComposedType.components` instead of a kind-driven type reference.

## Phase 4: Lexer And Lightweight Preprocessor

Branch target:

- `c-parser/phase-4-lexer`

Scope:

- Token/source normalization.
- Comments, continuations, directives, includes, simple macro metadata.
- No internal full macro expansion.
- Raw-source directive metadata first; compiler-assisted preprocessing is the
  required path when macros affect public declaration text.

### Lexer Tasks

- [x] Preserve original line numbers for all logical records.
- [x] Preserve original source lines for diagnostics.
- [x] Remove block comments `/* ... */` without losing line accounting.
- [x] Remove line comments `// ...`.
- [x] Avoid stripping comment markers inside string literals.
- [x] Avoid stripping comment markers inside character literals.
- [x] Handle escaped quotes inside literals.
- [x] Fold backslash-newline continuations.
- [x] Preserve preprocessor directive line locations.
- [x] Produce token records or logical line records with filename, line, column,
      and text.
- [x] Track braces, parentheses, and brackets.
- [x] Add top-level split helpers aware of nesting and literals.
- [x] Add tests for comment stripping.
- [x] Add tests for multiline block comments.
- [x] Add tests for string literal comment markers.
- [x] Add tests for char literal escapes.
- [x] Add tests for backslash-newline continuations.
- [x] Add tests for line/column preservation.

### Preprocessor Metadata Tasks

- [x] Recognize `#include "local.h"`.
- [x] Recognize `#include <system.h>`.
- [x] Store include spelling and include kind.
- [x] Resolve local includes relative to current file when possible.
- [x] Preserve unresolved includes as diagnostics, not hard errors by default.
- [x] Recognize object-like `#define NAME value`.
- [x] Recognize function-like `#define NAME(...) body`.
- [x] Store function-like macros as unsupported/deferred metadata.
- [x] Recognize `#undef`.
- [ ] Record conditional directive presence (`#ifdef`, `#ifndef`, `#if`,
      `#elif`, `#else`, `#endif`) as provenance metadata if needed.
- [x] Do not select active branches in raw mode.
- [ ] Do not implement a parser-side `defined(NAME)`, `&&`, `||`, `!`, `0`,
      and `1` evaluator for C API extraction unless a later design explicitly
      justifies it.
- [x] Mark macro-shaped declarations as unsupported/deferred in raw mode.
- [ ] Store macro-dependency metadata in C parser models.
- [x] Store preprocessing mode metadata in `CFile`.
- [ ] Store raw directive metadata separately from compiler-preprocessor
      configuration metadata.
- [x] Do not implement general macro expansion.
- [x] Do not expand token-paste or stringify macros.
- [x] Do not attempt recursive compiler-compatible macro expansion inside
      x2py.
- [x] Add tests for include collection.
- [x] Add tests for object-like macro collection.
- [x] Add tests for function-like macro diagnostics.
- [x] Add tests that raw conditional directives do not select active branches.
- [x] Add tests that macro-generated declarations are deferred in raw mode.

### Compiler-Assisted Preprocessing Tasks

- [ ] Design a preprocessed-input mode for `.i` files.
- [ ] Design an optional compiler invocation mode for `cc -E` or `clang -E`.
- [x] Document that compiler-assisted preprocessing is required when macros
      affect names, types, declarators, attributes, storage classes, calling
      conventions, visibility annotations, or active conditional branches.
- [ ] Preserve `#line` markers from compiler-preprocessed input.
- [ ] Map diagnostics from preprocessed declarations back to original files.
- [ ] Map parsed model `source_location` fields from preprocessed declarations
      back to original files.
- [ ] Mark preprocessed declarations with origin metadata.
- [ ] Store the preprocessor command/configuration in `CFile` or `CProject`.
- [ ] Store original and preprocessed source paths when both exist.
- [ ] Store macro defines, undefines, include dirs, and compiler/preprocessor
      executable used to produce the preprocessed stream.
- [ ] Add tests for parsing a simple `.i` file.
- [ ] Add tests for `#line` source mapping.
- [ ] Add tests that macro-generated declarations are parseable only when they
      appear in preprocessed input.

### Phase 4 Definition Of Done

- [x] Lexer/preprocessor preserves source locations.
- [x] Includes and macros are collected as metadata.
- [ ] Raw conditional directives are handled as metadata/provenance only, not
      parser-side branch selection.
- [x] No arbitrary macro expansion is attempted.
- [x] Compiler-assisted preprocessing has a documented design path for
      macro-heavy APIs.
- [ ] Tests cover comments, continuations, directive metadata, raw macro
      deferral, and preprocessed line mapping.

### Phase 4 Risks And Open Questions

- [x] Decide whether to tokenize fully now or keep logical records until
      declarator parsing requires tokens.
- [x] Decide whether system headers are recorded only or optionally searched.
- [ ] Decide whether `#pragma` should become diagnostics or metadata.
- [ ] Decide whether compiler invocation belongs in Phase 4 or a later
      project-resolution phase.

## Phase 5: Declarations And Declarators

Branch target:

- `c-parser/phase-5-declarations`

Scope:

- Shared C declaration parser.
- Declarator model and type construction.
- No broad function/project behavior beyond declarations.

### Declaration Specifier Tasks

- [x] Parse storage class `typedef`.
- [x] Parse storage class `extern`.
- [x] Parse storage class `static`.
- [x] Parse storage class `register`.
- [x] Parse storage class `_Thread_local`.
- [x] Parse qualifier `const`.
- [x] Parse qualifier `restrict`.
- [x] Parse qualifier `volatile`.
- [x] Parse qualifier `_Atomic` as basic metadata.
- [x] Parse `void`.
- [x] Parse `char`.
- [x] Parse `signed char`.
- [x] Parse `unsigned char`.
- [x] Parse `short`.
- [x] Parse `short int`.
- [x] Parse `unsigned short`.
- [x] Parse `int`.
- [x] Parse `unsigned`.
- [x] Parse `unsigned int`.
- [x] Parse `long`.
- [x] Parse `long int`.
- [x] Parse `unsigned long`.
- [x] Parse `long long`.
- [x] Parse `unsigned long long`.
- [x] Parse `float`.
- [x] Parse `double`.
- [x] Parse `long double`.
- [x] Parse `_Bool`.
- [x] Parse `_Complex` as deferred or supported with explicit tests.
- [x] Parse `struct name`.
- [x] Parse `union name`.
- [x] Parse `enum name`.
- [x] Parse typedef-name references.
- [x] Preserve original declaration specifier text.
- [x] Diagnose invalid primitive specifier sequences while deferring unresolved
      single typedef-name references to project/type resolution.

### Declarator Tasks

- [x] Parse identifier declarators.
- [x] Parse pointer declarators.
- [x] Parse pointer qualifiers.
- [x] Parse array declarators.
- [x] Parse multidimensional array declarators.
- [x] Parse static array parameter qualifiers, for example `int a[static 4]`.
- [x] Parse parenthesized declarators.
- [x] Parse function declarators.
- [x] Parse function pointer declarators.
- [x] Parse abstract declarators where needed for unnamed parameters.
- [x] Parse multiple declarators in one declaration.
- [x] Keep declarator entity order stable.
- [x] Preserve original declarator source text.
- [x] Add source locations for each declared entity.
- [x] Reject or diagnose unsupported declarator forms explicitly.

### Shared Declaration Backend Tasks

- [x] Implement a helper analogous to `_helper_parse_declaration_line`.
- [x] Feed procedure parameters through the same declaration backend.
- [x] Feed function return types through the same declaration backend.
- [x] Feed struct/union members through the same declaration backend.
- [x] Feed typedefs through the same declaration backend.
- [x] Feed file-scope variables/constants through the same declaration backend.
- [x] Apply declaration specifiers to declarator-derived type layers.
- [x] Normalize supported C type spelling into concrete `CType` subclasses.
- [x] Preserve typedef references before project resolution.
- [x] Add tests for each declaration role.
- [x] Add tests for declarations with multiple variables.
- [x] Add tests for declarations with initializers.
- [x] Add tests that local executable statements are not parsed as declarations.
- [x] Add exhaustive tests for every supported storage class.
- [x] Add exhaustive tests for every supported type qualifier.
- [x] Add exhaustive tests for every supported primitive spelling.
- [x] Add tests for typedef-name references outside `size_t`-style examples.
- [x] Add tests for `struct name`, `union name`, and `enum name` references in
      variables and parameters.
- [x] Add tests for multidimensional arrays.
- [ ] Add diagnostics for declarations ignored by the current partial parser.
- [ ] Add structured source facts for declarations that depend on macros.

Known declaration implementation gaps, with representative syntax:

- parameter array/function adjustment:
  `void process(int values[4], int callback(int));`
- braced/designated initializer preservation:
  `int values[3] = {1, 2, 3};`
- nested anonymous aggregate members:
  `struct outer { struct { int x; } inner; };`
- cross-declaration resolution/conflict behavior:
  `typedef unsigned long size_t; size_t count(void);`
- preprocessed declarations with line mapping:
  `#define API(ret) ret` followed by `API(int) run(void);`

Represented shapes still needing dedicated active regression tests:

- multi-level qualifier placement:
  `const int * const * volatile chain;`

### Phase 5 Definition Of Done

- [x] Shared declaration/declarator parser exists.
- [x] It is used by all declaration roles available so far.
- [x] Primitive, pointer, array, typedef-name, and tag references have tests.
- [ ] Unsupported declaration-shaped input raises `CParseError` or structured
      diagnostics.

### Phase 5 Risks And Open Questions

- [x] Represent the currently supported pointer/array/function declarator
      combinations as concrete type components and diagnose unconsumed forms.
- [x] Represent unresolved typedef-name uses as `CTypedef` type objects until
      project/type resolution is implemented.

## Phase 6: Function Parsing

Branch target:

- `c-parser/phase-6-functions`

Scope:

- Function prototypes and definitions.
- Signature extraction.
- Function body skipping by balanced brace slicing.

### Function Prototype Tasks

- [x] Classify top-level declarations ending with `;` as possible prototypes.
- [x] Parse return type through declaration/declarator backend.
- [x] Parse function name.
- [x] Parse ordered parameter list.
- [x] Preserve parameter names.
- [x] Preserve unnamed parameter types when legal.
- [x] Parse `void` parameter list as zero parameters.
- [x] Parse variadic marker `...`.
- [x] Mark `is_variadic`.
- [x] Parse pointer parameters.
- [x] Parse array parameters.
- [x] Parse function pointer parameters.
- [x] Parse `const` parameters.
- [x] Parse `restrict` parameters.
- [x] Parse `volatile` parameters.
- [x] Parse storage class `extern`.
- [x] Parse storage class `static`.
- [x] Add source locations.
- [x] Add tests for simple prototypes.
- [x] Add tests for no-argument prototypes.
- [x] Add tests for `void` arguments.
- [x] Add tests for pointer and array parameters.
- [x] Add tests for const pointer variants.
- [x] Add tests for variadic prototypes.
- [x] Add tests for function pointer parameters.
- [x] Add model field for prototype style so `int f(void)` and `int f()` can
      be distinguished.
- [x] Add tests that distinguish explicit `void` parameter lists from
      unspecified empty parameter lists.
- [x] Add parser source facts for variadic functions through `is_variadic`.
- [x] Add parser source facts for callback candidates once function pointer
      parameters are supported.

### Function Definition Tasks

- [x] Classify top-level declarator followed by `{` as function definition.
- [x] Parse signature from the definition header.
- [x] Preserve `is_definition=True`.
- [x] Preserve function-definition start/end locations.
- [x] Add direct `start`/`end` model fields before preserving definition
      ranges.
- [x] Skip function body contents for wrapper metadata.
- [x] Balance braces while respecting strings, chars, and comments.
- [x] Ignore local declarations for exported signatures in v1.
- [x] Reject or diagnose K&R style function definitions initially.
- [x] Add tests for simple definitions.
- [x] Add tests for nested braces in function body.
- [x] Add tests for strings containing braces.
- [x] Add tests for K&R unsupported diagnostics.
- [x] Detect K&R definitions before body skipping hides the old-style
      declaration list.

### Function Deduplication Tasks

- [ ] Merge matching prototype and definition in the same file.
- [ ] Prefer definition metadata where useful.
- [ ] Preserve both source locations if helpful.
- [ ] Detect conflicting declarations.
- [ ] Detect duplicate definitions.
- [ ] Allow same function under mutually exclusive preprocessor branches.
- [ ] Add tests for prototype plus definition.
- [ ] Add tests for conflicting prototypes.
- [ ] Add tests for duplicate definitions.
- [ ] Preserve declaration order before deduplicating prototypes and
      definitions.

### Phase 6 Definition Of Done

- [x] Basic C function signatures parse from `.h` and `.c`.
- [x] Function bodies are skipped safely.
- [x] Variadic and supported function pointer cases are represented as typed
      source facts.
- [x] CLI human and JSON output show functions.
- [ ] Parser diagnostics report no-functions only when appropriate.

### Phase 6 Risks And Open Questions

- [ ] Decide whether inline functions in headers are definitions or prototypes
      for wrapper purposes.
- [ ] Decide how to handle attributes in function declarations before full
      extension support exists.

## Phase 7: Structs, Unions, Enums, And Typedefs

Branch target:

- `c-parser/phase-7-structs-enums`

Scope:

- C composite types and typedef aliases.

### Struct Tasks

- [x] Parse named `struct name { ... };`.
- [x] Parse forward declaration `struct name;`.
- [x] Parse anonymous `struct { ... }`.
- [x] Parse typedef anonymous struct `typedef struct { ... } name;`.
- [x] Parse typedef named struct `typedef struct tag name;`.
- [x] Parse members with shared declaration backend.
- [x] Parse pointer members.
- [x] Parse array members, including legal flexible final struct members with
      invalid-placement and union diagnostics.
- [x] Parse nested anonymous structs as unsupported or metadata.
- [x] Parse bit-fields as member metadata with semantic limitations.
- [x] Preserve member order.
- [x] Preserve precise per-member source locations.
- [x] Mark incomplete structs.
- [x] Add tests for named structs.
- [x] Add tests for forward declarations.
- [x] Add tests for typedef structs.
- [x] Add tests for pointer members.
- [x] Add tests for array members.
- [x] Add tests for named, unnamed, and zero-width bit-field source facts and
      locations; defer ABI/wrappability diagnostics to the semantic layer.

### Union Tasks

- [x] Parse named unions.
- [x] Parse forward union declarations.
- [x] Parse anonymous unions.
- [x] Parse typedef unions.
- [x] Parse union members with shared declaration backend.
- [x] Retain union member ownership through the containing `CUnion`.
- [ ] Add diagnostics for by-value unions if unsafe.
- [x] Add tests for named unions.
- [x] Add tests for typedef unions.
- [ ] Add tests for union diagnostics.

### Enum Tasks

- [x] Parse named enums.
- [x] Parse anonymous enums.
- [x] Parse typedef enums.
- [x] Parse enumerator names.
- [x] Parse explicit enumerator values.
- [x] Preserve symbolic enumerator values.
- [ ] Safely fold simple integer expressions.
- [x] Preserve expression text when folding is unsafe.
- [x] Add tests for plain enums.
- [x] Add tests for explicit values.
- [x] Add tests for expression values.
- [x] Add tests for typedef enums.

### Typedef Tasks

- [x] Parse primitive typedefs.
- [x] Parse pointer typedefs.
- [x] Parse array typedefs.
- [x] Parse function pointer typedefs.
- [x] Parse struct/union/enum typedefs.
- [x] Preserve alias chains before resolution.
- [ ] Detect duplicate typedefs in same scope.
- [x] Add tests for typedef chains.
- [x] Add tests for primitive typedefs.
- [x] Add tests for opaque handle typedefs.
- [ ] Add tests for function pointer typedef diagnostics.

### Phase 7 Definition Of Done

- [x] C composite and typedef models are populated from basic fixtures.
- [x] Shared declaration backend handles members and typedefs.
- [x] Validate legal and invalid flexible-array-member placement and retain
      named, unnamed, and zero-width bit-field source facts with tests.
- [ ] JSON goldens cover composite type schema.
- [x] Docs list supported and unsupported composite forms.

### Phase 7 Risks And Open Questions

- [x] Decide when anonymous structs should become generated internal names.
- [ ] Decide how much enum expression folding is safe without compiler
      semantics.
- [ ] Decide how unions map to semantic IR, if at all in v1.

## Phase 8: Include And Project Resolution

Branch target:

- `c-parser/phase-8-project-resolution`

Scope:

- Multi-file project parsing.
- Include graph.
- Type and typedef resolution.

### File Discovery Tasks

- [x] Discover `.c` files in C mode.
- [x] Discover `.h` files in C mode.
- [ ] Decide whether `.i` is included now or later.
- [x] Keep Fortran directory scanning unchanged.
- [x] Support explicit file lists.
- [x] Support directory recursion only in explicit C mode.
- [x] Preserve deterministic file ordering.
- [x] Add tests for file discovery.

### Include Resolution Tasks

- [ ] Resolve quoted includes relative to current file.
- [ ] Resolve quoted includes through `include_dirs`.
- [ ] Record unresolved quoted includes.
- [ ] Record system includes without requiring local resolution by default.
- [ ] Build `include_graph`.
- [ ] Detect include cycles without crashing.
- [ ] Preserve include spelling and resolved path separately.
- [ ] Add tests for local includes.
- [ ] Add tests for include dirs.
- [ ] Add tests for missing includes.
- [ ] Add tests for include cycles.

### Project Index Tasks

- [x] Index functions by name.
- [ ] Index functions by file.
- [x] Index typedefs by name.
- [x] Index struct tags by tag namespace.
- [x] Index union tags by tag namespace.
- [x] Index enum tags by tag namespace.
- [ ] Index enum constants in ordinary identifier namespace.
- [x] Index macros/constants separately.
- [x] Index variables by name.
- [ ] Detect duplicate definitions.
- [ ] Distinguish compatible redeclarations from conflicts.
- [ ] Add tests for duplicate handling.
- [ ] Add tests for project-level function indexes.
- [ ] Add tests for project-level typedef indexes.
- [ ] Add tests for project-level file-scope variable indexes.
- [ ] Add tests for project-level macro indexes.

### Type Resolution Tasks

- [ ] Resolve typedef chains.
- [ ] Detect typedef cycles.
- [ ] Resolve struct tag references.
- [ ] Resolve union tag references.
- [ ] Resolve enum tag references.
- [ ] Resolve opaque pointer typedefs.
- [ ] Preserve unresolved references for later semantic diagnostics.
- [ ] Do not lose original spelling during resolution.
- [ ] Add tests for cross-file typedef resolution.
- [ ] Add tests for cross-file struct resolution.
- [ ] Add tests for opaque handles.
- [ ] Add tests for unresolved references.

### Header/Source Pairing Tasks

- [ ] Pair `foo.c` with `foo.h` by basename.
- [ ] Pair source with headers it includes.
- [ ] Preserve many-to-many relationships.
- [ ] Use pairings for reporting, not for hidden behavior.
- [ ] Add tests for header/source pairing.

### Phase 8 Definition Of Done

- [ ] `parse_c_project` returns a populated `CProject`.
- [ ] Include graph is stable and serialized.
- [ ] Cross-file typedef/tag resolution works for basic projects.
- [ ] Missing project context becomes parser or semantic diagnostics as
      appropriate.
- [ ] Tests cover directory and file-list parsing.

### Phase 8 Risks And Open Questions

- [ ] Decide whether project parsing should parse all included system headers
      when found.
- [ ] Decide how to handle generated headers.
- [ ] Decide whether include graph should be path-keyed, module-keyed, or both.

## Phase 9: Semantic Readiness Integration

Branch target:

- `c-parser/phase-9-semantic-readiness`

Scope:

- Semantic readiness integration for C parser facts.
- File-level and unit-level blockers, but owned by the semantic layer rather
  than the parser.

### Readiness Schema Tasks

- [ ] Define stable C readiness dictionary keys for the semantic layer.
- [ ] Include counts for functions, structs, unions, enums, typedefs, macros,
      includes, and diagnostics.
- [ ] Include `unsupported_constructs`.
- [ ] Include `unresolved_includes`.
- [ ] Include `unresolved_typedefs`.
- [ ] Include `unresolved_tags`.
- [ ] Include `macro_dependent_declarations`.
- [ ] Include `preprocessing_origin`.
- [ ] Include `unsupported_extensions`.
- [ ] Include `ambiguous_pointer_ownership`.
- [ ] Include `ambiguous_array_extents`.
- [ ] Include `callback_functions`.
- [ ] Include `variadic_functions`.
- [ ] Include `incomplete_public_types`.
- [ ] Include `wrappability_blockers`.
- [ ] Include `unit_blockers`.
- [ ] Include `why_not_wrappable`.
- [ ] Include file-level `wrappable`.

### Diagnostic Tasks

- [ ] Report no functions found.
- [ ] Report unresolved includes.
- [ ] Report unresolved typedefs.
- [ ] Report unresolved struct tags.
- [ ] Report unresolved union tags.
- [ ] Report unresolved enum tags.
- [ ] Report incomplete structs used by value.
- [ ] Report incomplete unions used by value.
- [ ] Report variadic functions.
- [ ] Report K&R functions.
- [ ] Report function pointer return types.
- [ ] Report function pointer parameters.
- [ ] Report callback typedef parameters.
- [ ] Report missing callback `.pyi` policy.
- [ ] Report macro-dependent declarations.
- [ ] Report unsupported attributes.
- [ ] Report unsupported compiler extensions.
- [ ] Report unsupported bitfields.
- [ ] Report pointer ownership ambiguity.
- [ ] Report non-const pointer mutability ambiguity.
- [ ] Report arrays with unknown extent relationships.
- [ ] Report opaque pointers as warning or non-blocker if policy allows.

### Unit Blocker Tasks

- [ ] Assign function blockers to function units.
- [ ] Assign struct field blockers to struct units.
- [ ] Assign union field blockers to union units.
- [ ] Assign enum value blockers to enum units.
- [ ] Assign typedef blockers to typedef units.
- [ ] Assign include/macro/file-scope-variable blockers to file units when no narrower owner
      exists.
- [ ] Use qualified names where available.
- [ ] Avoid per-unit ready flags; keep readiness file-level like Fortran.
- [ ] Add tests for every blocker family.
- [ ] Add semantic readiness formatting tests.

### Phase 9 Definition Of Done

- [ ] Readiness output is stable in JSON and human CLI when served by the
      semantic layer.
- [ ] Diagnostics identify exactly which units block wrapping.
- [ ] Common unsupported C constructs produce actionable messages.
- [ ] Docs list readiness codes and examples.
- [ ] Tests cover readiness families.

### Phase 9 Risks And Open Questions

- [ ] Decide which pointer cases are blockers versus warnings.
- [ ] Decide how semantic readiness should treat opaque handles.
- [ ] Decide the exact readiness code names for callback APIs that are parsed
      but missing user-supplied `.pyi` policy.

## Phase 10: Semantic IR Conversion

Branch target:

- `c-parser/phase-10-semantics`

Scope:

- Convert C parser models into language-independent semantic IR.

### Converter Structure Tasks

- [ ] Create `semantics/c2ir.py`.
- [ ] Implement `CToIRConverter`.
- [ ] Mirror the visitor style of `FortranToIRConverter`.
- [ ] Add compatibility helpers such as `c_file_to_semantic_modules`.
- [ ] Add `c_function_to_semantic_function`.
- [ ] Add `c_struct_to_semantic_class` where appropriate.
- [ ] Add `c_project_to_semantic_modules` if project context is needed.
- [ ] Keep conversion separate from parser internals.

### Type Mapping Tasks

- [ ] Map `void` return to `None`.
- [ ] Map `_Bool` to `Bool`.
- [ ] Map `char` to an explicit semantic type policy.
- [ ] Map signed integer widths.
- [ ] Map unsigned integer widths.
- [ ] Map `float` to `Float32`.
- [ ] Map `double` to `Float64`.
- [ ] Map `long double` to a documented type or unsupported diagnostic.
- [ ] Map pointers to constraints/metadata.
- [ ] Map arrays to `Shape` and `ORDER_C`.
- [ ] Map `const` to read-only/ownership metadata.
- [ ] Map `restrict` to aliasing metadata.
- [ ] Map structs to semantic classes or named semantic types.
- [ ] Map unions conservatively.
- [ ] Map enums/constants.
- [ ] Preserve unresolved semantic types as errors, not `Unknown` output.

### Function Projection Tasks

- [ ] Convert C functions to `SemanticFunction`.
- [ ] Preserve native function name.
- [ ] Preserve parameter order.
- [ ] Mark pointer mutability.
- [ ] Represent array pointer plus size patterns only when known.
- [ ] Add projection metadata only where native and Python signatures diverge.
- [ ] Treat out parameters conservatively until ownership/intent policy exists.
- [ ] Reject or defer variadic functions.
- [ ] Preserve callback/function-pointer facts from C parser models even if
      semantic conversion defers wrapper generation.
- [ ] Defer callback conversion unless `.pyi` policy supplies the required
      callback facts.
- [ ] Add semantic tests for scalar functions.
- [ ] Add semantic tests for pointer input.
- [ ] Add semantic tests for const pointer input.
- [ ] Add semantic tests for arrays with explicit size parameter.
- [ ] Add semantic tests for structs/opaque handles.

### Phase 10 Definition Of Done

- [ ] C semantic conversion works for the supported parser subset.
- [ ] Unsupported C semantic mappings fail explicitly.
- [ ] `--language c --semantics` can be enabled with tests.
- [ ] Semantic fixture workflow exists for C if stable enough.
- [ ] Docs explain C to semantic IR mapping.

### Phase 10 Risks And Open Questions

- [ ] Current semantic IR may need richer pointer/ownership constraints.
- [ ] Unsigned integer semantic type names may need standardization.
- [ ] Struct/union/enum representation may require semantic model extensions.

## Phase 11: `.pyi` Generation And Parsing Integration

Branch target:

- `c-parser/phase-11-pyi`

Scope:

- Emit/edit semantic interface stubs for C APIs.
- Extend `.pyi` syntax only through semantic IR needs.

### Generation Tasks

- [ ] Enable `--language c --pyi` only after semantic conversion is stable.
- [ ] Generate stubs from C semantic modules.
- [ ] Emit scalar functions.
- [ ] Emit pointer constraints when semantic model supports them.
- [ ] Emit arrays with `ORDER_C`.
- [ ] Emit constants as `Final[...]`.
- [ ] Emit opaque handles as classes or semantic type annotations.
- [ ] Emit structs as classes only when field semantics are intended.
- [ ] Avoid emitting `Unknown`.
- [ ] Emit imports/includes only if represented in semantic IR.
- [ ] Add tests for scalar function stubs.
- [ ] Add tests for constant stubs.
- [ ] Add tests for opaque handle stubs.
- [ ] Add tests for array stubs.

### Parser Integration Tasks

- [ ] Confirm existing `.pyi` parser accepts generated C stubs.
- [ ] Extend `.pyi` parser only if semantic IR requires new constructs.
- [ ] Add round-trip tests for C-generated stubs.
- [ ] Add edited-stub tests for C APIs.
- [ ] Add tests that unsupported C stubs fail clearly.
- [ ] Add fixture tests under `tests/pyi/fixtures/c/` if C stubs are stable.

### Native Projection Tasks

- [ ] Represent pointer/size hidden relationships where known.
- [ ] Represent returned output buffers only with explicit projection metadata.
- [ ] Represent ownership/lifetime metadata if supported by IR.
- [ ] Define `.pyi` policy fields for callback signatures.
- [ ] Define `.pyi` policy fields for callback direction.
- [ ] Define `.pyi` policy fields for call-only versus stored callback
      lifetime.
- [ ] Define `.pyi` policy fields for context/userdata pairing.
- [ ] Define `.pyi` policy fields for callback nullability.
- [ ] Define `.pyi` policy fields for non-default calling conventions.
- [ ] Define `.pyi` policy fields for threading and async invocation.
- [ ] Define `.pyi` policy fields for ownership of callback/context memory.
- [ ] Define `.pyi` policy fields for release/unregistration APIs.
- [ ] Define `.pyi` policy fields for Python exception/error handling.
- [ ] Defer callback projection until those policy fields are supplied by the
      user.
- [ ] Defer arbitrary ABI details.

### Phase 11 Definition Of Done

- [ ] C `.pyi` output works for supported semantic subset.
- [ ] Generated stubs parse back into semantic IR.
- [ ] C `.pyi` tests are separate from Fortran `.pyi` tests.
- [ ] Docs describe generated C stub shape and limitations.

### Phase 11 Risks And Open Questions

- [ ] Existing `.pyi` syntax may not be expressive enough for ownership and
      lifetimes.
- [ ] Opaque handles might require new conventions.
- [ ] C callbacks likely need dedicated `.pyi` policy syntax and later semantic
      IR extensions.

## Phase 12: Corpus Testing, Stabilization, And Regression Hardening

Branch target:

- `c-parser/phase-12-corpus-stabilization`

Scope:

- Harden parser against realistic C APIs.
- Stabilize docs, tests, schema, and CLI.
- Prepare eventual mature integration.

### Corpus Tasks

- [ ] Use cJSON as the first pinned real-world C corpus target.
- [ ] Pin cJSON to an exact tag or commit rather than tracking the moving
      default branch.
- [ ] Store cJSON provenance in `tests/data/c/corpus/cjson/SOURCE.md`.
- [ ] Store cJSON license text next to the vendored fixture files.
- [ ] Add `tests/data/c/corpus/cjson/cJSON.h`.
- [ ] Add `tests/data/c/corpus/cjson/cJSON.c`.
- [ ] Treat cJSON corpus tests as parse-only at first.
- [ ] Use cJSON to exercise typedef structs, recursive pointers, `const char *`
      APIs, `size_t`, public declaration macros, numeric/string constants,
      and callback hook members.
- [ ] Keep callback hook members modeled in `c_parser/models.py`, with
      semantic readiness requiring explicit user `.pyi` callback policy metadata
      before claiming they are wrappable.
- [ ] Add zlib or another macro-heavier C library only after
      compiler-assisted preprocessing mode is available.
- [ ] Add small real-world C header corpus.
- [ ] Add scientific C API fixtures.
- [ ] Add source/header project fixtures.
- [ ] Add macro-heavy unsupported fixtures.
- [ ] Add callback fixtures.
- [ ] Add variadic function fixtures.
- [ ] Add opaque handle fixtures.
- [ ] Add array-size pattern fixtures.
- [ ] Add typedef-chain fixtures.
- [ ] Add parse-only corpus tests.
- [ ] Add selected parser JSON goldens for representative corpus files.
- [ ] Keep corpus license provenance documented.

### Regression Hardening Tasks

- [ ] Run full parser tests.
- [ ] Run semantic tests.
- [ ] Run `.pyi` tests.
- [ ] Run C corpus parse-only tests.
- [x] Run CLI tests.
- [ ] Run golden fixture tests.
- [ ] Confirm Fortran tests still pass.
- [ ] Audit JSON schema stability.
- [ ] Audit error diagnostic stability.
- [x] Audit docs for implemented behavior.
- [x] Remove stale skeleton wording where implementation has matured.
- [ ] Add developer tutorial for C parser internals.
- [ ] Add public API reference examples.

### Stabilization Tasks

- [ ] Decide criteria for merging `c-parser/main` into project `main`.
- [ ] Require green CI for Fortran and C suites.
- [ ] Require docs updated for implemented subset.
- [ ] Require fixture/golden workflow documented.
- [ ] Require semantic and `.pyi` behavior documented.
- [ ] Require explicit non-goals still documented.
- [ ] Require migration notes for users.
- [ ] Consider adding CI guard requiring C parser docs updates for C parser
      changes, mirroring the Fortran parser reference policy.

### Phase 12 Definition Of Done

- [ ] C parser handles a representative stable subset.
- [ ] CLI, JSON, semantic readiness, semantic IR, and `.pyi` workflows are
      tested.
- [ ] Fixture/golden workflows are stable.
- [ ] Corpus tests catch regressions.
- [ ] Fortran behavior remains stable.
- [ ] `c-parser/main` is mature enough to consider a planned merge to project
      `main`.

### Phase 12 Risks And Open Questions

- [ ] Scope creep toward compiler-grade parsing.
- [ ] Macro-heavy APIs require clear raw-source versus compiler-preprocessed
      mode behavior.
- [ ] Ownership/lifetime semantics may need broader IR work.
- [ ] C extensions may need fixture-driven prioritization.

## Cross-Phase Non-Goals For V1

- [ ] Do not support full compiler-grade C parsing.
- [ ] Do not support full C preprocessor compatibility.
- [ ] Do not support arbitrary macro expansion.
- [ ] Do not parse macro-generated declarations from raw source as if they were
      ordinary C declarations.
- [ ] Do not support token-paste/stringify expansion.
- [ ] Do not support all compiler extensions.
- [ ] Do not support arbitrary GCC extensions.
- [ ] Do not support arbitrary MSVC extensions.
- [ ] Do not parse C++.
- [ ] Do not generate a full ABI model.
- [ ] Do not infer pointer ownership silently.
- [ ] Do not claim callbacks are safely wrappable before the required `.pyi`
      callback policy is supplied.
- [ ] Do not modify Fortran parser behavior as part of C parser work unless a
      shared change is explicitly planned, tested, and documented.
