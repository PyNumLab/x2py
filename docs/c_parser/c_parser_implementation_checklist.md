# C Parser Implementation Checklist

Status: planning checklist. No parser implementation exists in this branch yet.

This checklist is intentionally detailed so future work can proceed one branch,
one checklist item, and one tested capability at a time. The C parser initiative
must remain isolated from project `main` until the frontend is mature and
stable.

## Global Rules

- [ ] Keep all C parser work on `c-parser/main` and child branches until the
      frontend is stable.
- [ ] Do not merge C parser work directly into project `main`.
- [ ] Keep the Fortran parser behavior unchanged unless a future task
      explicitly requires shared infrastructure changes.
- [ ] Put C parser implementation in a separate `c_parser` package.
- [ ] Keep C parser tests separated from existing Fortran tests.
- [ ] Gate all integration through explicit C flags or C-specific APIs.
- [ ] Keep the C parser main-merge guard active for C parser branches and
      paths.
- [ ] Require the `c-parser-ready-for-main` label only for the final approved
      merge into project `main`.
- [ ] Do not implement a giant regex parser.
- [ ] Do not implement a whole-file scanner as the core architecture.
- [ ] Do not make libclang the only parser architecture.
- [ ] Preserve the semantic IR layer as the source of truth.
- [ ] Treat documentation as a first-class deliverable in every phase.
- [ ] Update this checklist when implementation reality changes.

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
- [x] Inspect wrap-readiness tests.
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
- [x] Document readiness diagnostics direction.
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

- [ ] Decide whether the future package should be named `c_parser` or another
      name before code lands.
- [ ] Decide whether `x2py.__init__` should expose C APIs during skeleton phase
      or wait until Phase 3 models are useful.
- [ ] Decide whether C debug env var should be `C_PARSER_DEBUG` or generic
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

- [ ] Update `docs/c_parser/c_parser_cli_workflow.md` with implemented command
      examples.
- [ ] Update `docs/c_parser/c_parser_reference.md` with skeleton CLI behavior.
- [ ] Add a "Current Status" section showing which C features are placeholder
      only.
- [ ] Document how C parser output differs from Fortran parser output.
- [ ] Document that auto-detection is deferred.
- [ ] Document that `--language c` is required initially.
- [ ] Document unsupported `--semantics --language c` behavior.
- [ ] Document unsupported `--pyi --language c` behavior.
- [ ] Document C parser diagnostics even if only skeleton diagnostics exist.
- [ ] Add examples for parse tree, JSON, readiness, and output file behavior.

### CLI Design Tasks

- [ ] Add `--language {fortran,c}` to `x2py.cli`.
- [ ] Preserve current Fortran behavior when `--language` is omitted.
- [ ] Make `--language fortran` equivalent to current behavior.
- [ ] Add explicit C parse path behind `--language c --parse`.
- [ ] Decide whether to add `--parse-c` alias in this phase.
- [ ] If `--parse-c` is added, make it an alias for `--language c --parse`.
- [ ] Reject `--language c` without a supported stage flag.
- [ ] Reject `--language c --semantics` until Phase 10.
- [ ] Reject `--language c --pyi` until Phase 11.
- [ ] Reject Fortran-only flags in C mode if they do not apply.
- [ ] Keep `--wrap-readiness` requiring `--parse`.
- [ ] Keep `--json` behavior stable for parse output.
- [ ] Keep `--out` behavior stable for C parse JSON.
- [ ] Keep `--no-color` accepted in C mode.
- [ ] Keep `--debug-traceback` accepted in C mode.
- [ ] Do not change `fortran_parser.cli` unless a compatibility reason is
      documented.

### Skeleton Report Tasks

- [ ] Create a minimal C report provider without real parsing.
- [ ] Ensure skeleton C report can accept `.c` and `.h` paths.
- [ ] Ensure skeleton C report can accept directories only in explicit C mode.
- [ ] Return `language: "c"` in C JSON output.
- [ ] Return `parser_status: "skeleton"` in C JSON output.
- [ ] Return empty `functions` list.
- [ ] Return empty `structs` list.
- [ ] Return empty `unions` list.
- [ ] Return empty `enums` list.
- [ ] Return empty `typedefs` list.
- [ ] Return empty `globals` list.
- [ ] Return empty `macros` list.
- [ ] Return empty `includes` list.
- [ ] Return empty `diagnostics` list unless a skeleton diagnostic is needed.
- [ ] Return readiness with `wrappable: false`.
- [ ] Include a `parser_skeleton` blocker.
- [ ] Human tree output should show zero-count C sections and skeleton status.
- [ ] Readiness output should show the skeleton blocker.

### CLI Test Tasks

- [ ] Add C CLI tests in a C-specific test file, for example
      `tests/parser/test_c_cli_skeleton.py` or `tests/c_parser/test_cli.py`.
- [ ] Test existing Fortran CLI behavior still passes.
- [ ] Test `--help` shows `--language`.
- [ ] Test `--language c --parse` accepts a temporary `.h` file.
- [ ] Test `--language c --parse --json` emits valid JSON.
- [ ] Test `--language c --parse --wrap-readiness` emits stable readiness.
- [ ] Test `--language c --parse --out report.json` writes JSON and suppresses
      stdout.
- [ ] Test `--language c --semantics` returns argparse error or clear
      unsupported-stage error.
- [ ] Test `--language c --pyi` returns argparse error or clear
      unsupported-stage error.
- [ ] Test `--language c --parse --show-vars` is rejected or ignored with
      documented behavior.
- [ ] Test `--parse` without `--language` remains Fortran behavior.
- [ ] If `--parse-c` is added, test it maps to C parse mode.
- [ ] Test `--no-color` is accepted in C mode.
- [ ] Test `NO_COLOR=1` is honored once C diagnostics exist.
- [ ] Test `--debug-traceback` is accepted in C mode.

### Phase 1 Definition Of Done

- [ ] Users can discover C mode from CLI help.
- [ ] Users can run a stable C parse skeleton command.
- [ ] C JSON skeleton output has a documented schema.
- [ ] C readiness skeleton output is stable and not falsely wrappable.
- [ ] Fortran CLI behavior is unchanged.
- [ ] Documentation includes the exact command workflow.
- [ ] Tests cover the skeleton command workflow.

### Phase 1 Risks And Open Questions

- [ ] Decide whether to implement a temporary skeleton module inside
      `x2py.cli` or create `c_parser/cli.py` early.
- [ ] Decide whether skeleton output should include zero-count sections in
      human output or omit empty sections like Fortran.
- [ ] Decide whether `--json` should eventually support semantic C output or
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

- [ ] Create a dedicated C parser test area.
- [ ] Choose between `tests/c_parser/` and `tests/parser/c/` for focused C
      parser tests.
- [ ] Create `tests/data/c/general/`.
- [ ] Create `tests/data/c/errors/parser/`.
- [ ] Create `tests/data/c/corpus/`.
- [ ] Create `tests/data/c/scientific/`.
- [ ] Create `tests/parser/c/fixtures/general/`.
- [ ] Create `tests/parser/c/fixtures/errors/`.
- [ ] Keep C fixture data separate from Fortran fixture data.
- [ ] Add README files explaining each C fixture directory.
- [ ] Add small placeholder `.h` and `.c` fixture files only if tests need them.

### Skipped Roadmap Test Policy

- [x] Add skipped C parser roadmap tests before implementation starts.
- [x] Keep every roadmap test skipped until its implementation branch lands.
- [x] Keep `c_parser` imports inside skipped test functions, not at module
      import time, so collection works before the package exists.
- [x] Use the skipped tests as an executable checklist for future branches.
- [ ] Unskip tests one capability at a time.
- [ ] In each implementation branch, unskip only the tests covered by that
      branch.
- [ ] Do not unskip broad fixture, corpus, semantic, or `.pyi` tests before
      the supporting workflow exists.
- [ ] When a skipped test is unblocked, replace placeholder expectations with
      the exact implemented model fields if the final schema differs.
- [ ] Keep the skipped C suite separate from existing Fortran tests.
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
- [x] Create `tests/parser/c/test_c_wrap_readiness.py`.
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

- [ ] Add lexer test file.
- [ ] Add preprocessor test file.
- [ ] Add declaration-specifier test file.
- [ ] Add declarator test file.
- [ ] Add function parser test file.
- [ ] Add struct/union/enum parser test file.
- [ ] Add typedef parser test file.
- [ ] Add macro/constant parser test file.
- [ ] Add project/include parser test file.
- [ ] Add readiness test file.
- [ ] Add public entrypoint test file.
- [ ] Add developer tutorial test file once internal helpers exist.
- [ ] Add CLI test file.
- [ ] Add fixture/golden test file.
- [ ] Add error fixture/golden test file.
- [ ] Add semantic conversion tests in Phase 10.
- [ ] Add `.pyi` tests in Phase 11.

### Phase 2 Definition Of Done

- [ ] C test directory structure is present.
- [ ] C fixture directory structure is present.
- [ ] C golden update workflow is documented.
- [ ] Placeholder tests pass against skeleton behavior.
- [ ] Fortran tests still pass.
- [ ] No real parser claims are made without tests.

### Phase 2 Test Expectations

- [x] Run the skipped C roadmap suite and confirm it collects without importing
      `c_parser` at module import time.
- [ ] Run C skeleton CLI tests.
- [ ] Run existing parser CLI tests.
- [ ] Run a small targeted test command, for example
      `python -m pytest -q tests/parser/test_cli.py tests/parser/test_c_cli_skeleton.py`.
- [ ] Do not update Fortran goldens.

### Phase 2 Risks And Open Questions

- [ ] Decide how much C fixture data is appropriate before parser behavior
      exists.
- [ ] Decide whether C parser tests should live alongside Fortran parser tests
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

- [ ] Create `c_parser/__init__.py`.
- [ ] Create `c_parser/__main__.py`.
- [ ] Create `c_parser/models.py`.
- [ ] Create `c_parser/parser.py`.
- [ ] Create `c_parser/lexer.py`.
- [ ] Create `c_parser/preprocessor.py`.
- [ ] Create `c_parser/type_resolver.py`.
- [ ] Create `c_parser/project.py`.
- [ ] Create `c_parser/cli.py`.
- [ ] Create `c_parser/utils.py`.
- [ ] Add `c_parser*` to package discovery in `pyproject.toml`.
- [ ] Add `c_parser` to coverage source when implementation begins.
- [ ] Keep imports from `x2py.cli` explicit and isolated.

### Error Model Tasks

- [ ] Implement `CParseError` as a `ValueError` subclass.
- [ ] Include `filename`.
- [ ] Include `line_number`.
- [ ] Include `column`.
- [ ] Include `source_line`.
- [ ] Include `base_message`.
- [ ] Include `code`.
- [ ] Include parser raise location for debug diagnostics.
- [ ] Implement `format_diagnostic(color=False, debug=None)`.
- [ ] Use C diagnostic code prefix such as `CPARSE001`.
- [ ] Add color handling equivalent to `FortranParseError`.
- [ ] Add optional C debug env var.
- [ ] Test C parse error attributes.
- [ ] Test compiler-style diagnostic rendering.
- [ ] Test color and no-color behavior.
- [ ] Test debug note behavior.

### Model Tasks

- [ ] Define `CSourceLocation`.
- [ ] Define `CDiagnostic`.
- [ ] Define `CTypeRef`.
- [ ] Define `CPointer`.
- [ ] Define `CArray`.
- [ ] Define `CParameter`.
- [ ] Define `CFunction`.
- [ ] Define `CField`.
- [ ] Define `CStruct`.
- [ ] Define `CUnion` or use `CStruct(is_union=True)`.
- [ ] Define `CEnum`.
- [ ] Define `CEnumerator`.
- [ ] Define `CTypedef`.
- [ ] Define `CGlobal`.
- [ ] Define `CMacro`.
- [ ] Define `CInclude`.
- [ ] Define `CFile`.
- [ ] Define `CProject`.
- [ ] Define `CWrapReadinessReport` only if a dataclass helps; otherwise use
      stable dictionaries like Fortran readiness.
- [ ] Add helper properties for pointer depth.
- [ ] Add helper properties for array rank.
- [ ] Add helper properties for effective type text.
- [ ] Add helper properties for `is_const_pointer`.
- [ ] Add helper properties for `is_opaque_type`.
- [ ] Add helper properties for source-location display.

### Serialization Tasks

- [ ] Add `_to_dict` or equivalent serialization helper.
- [ ] Avoid cycles in JSON.
- [ ] Keep source locations JSON-serializable.
- [ ] Decide whether sets serialize as sorted lists.
- [ ] Ensure dataclass defaults produce stable JSON.
- [ ] Add tests for empty `CFile` serialization.
- [ ] Add tests for each model's minimal JSON shape.
- [ ] Add tests for source-location serialization.
- [ ] Add tests that unknown/unresolved metadata is preserved.

### Public API Skeleton Tasks

- [ ] Implement `CParser` class.
- [ ] Implement `CParser.visit_file` returning skeleton or model-only `CFile`.
- [ ] Implement `CParser.visit_project` returning skeleton/model-only
      `CProject`.
- [ ] Implement `CParser.visit_wrap_readiness`.
- [ ] Implement module-level `_DEFAULT_PARSER`.
- [ ] Implement `parse_c_file`.
- [ ] Implement `parse_c_project`.
- [ ] Implement `assess_c_wrap_readiness`.
- [ ] Add public API tests for source strings.
- [ ] Add public API tests for file paths.
- [ ] Add public API tests for empty source.
- [ ] Add public API tests for unknown suffix.

### Phase 3 Definition Of Done

- [ ] `c_parser` imports cleanly.
- [ ] Skeleton public APIs return typed models.
- [ ] JSON serialization is stable and tested.
- [ ] C CLI uses `c_parser` rather than a temporary inline provider.
- [ ] Fortran parser API remains unchanged.
- [ ] Docs describe the new package and API status.

### Phase 3 Risks And Open Questions

- [ ] Decide whether `CUnion` should subclass/share `CStruct`.
- [ ] Decide how to represent anonymous structs/unions/enums.
- [ ] Decide whether macros belong in `CFile.macros` only or also symbols.
- [ ] Decide whether `CTypeRef` should be a single recursive model or contain
      normalized pointer/array/function layers.

## Phase 4: Lexer And Lightweight Preprocessor

Branch target:

- `c-parser/phase-4-lexer`

Scope:

- Token/source normalization.
- Comments, continuations, directives, includes, simple macro metadata.
- No internal full macro expansion.
- Raw-source parsing first; compiler-assisted preprocessing path planned for
  macro-heavy APIs.

### Lexer Tasks

- [ ] Preserve original line numbers for all logical records.
- [ ] Preserve original source lines for diagnostics.
- [ ] Remove block comments `/* ... */` without losing line accounting.
- [ ] Remove line comments `// ...`.
- [ ] Avoid stripping comment markers inside string literals.
- [ ] Avoid stripping comment markers inside character literals.
- [ ] Handle escaped quotes inside literals.
- [ ] Fold backslash-newline continuations.
- [ ] Preserve preprocessor directive line locations.
- [ ] Produce token records or logical line records with filename, line, column,
      and text.
- [ ] Track braces, parentheses, and brackets.
- [ ] Add top-level split helpers aware of nesting and literals.
- [ ] Add tests for comment stripping.
- [ ] Add tests for multiline block comments.
- [ ] Add tests for string literal comment markers.
- [ ] Add tests for char literal escapes.
- [ ] Add tests for backslash-newline continuations.
- [ ] Add tests for line/column preservation.

### Preprocessor Metadata Tasks

- [ ] Recognize `#include "local.h"`.
- [ ] Recognize `#include <system.h>`.
- [ ] Store include spelling and include kind.
- [ ] Resolve local includes relative to current file when possible.
- [ ] Preserve unresolved includes as diagnostics, not hard errors by default.
- [ ] Recognize object-like `#define NAME value`.
- [ ] Recognize function-like `#define NAME(...) body`.
- [ ] Store function-like macros as unsupported/deferred metadata.
- [ ] Recognize `#undef`.
- [ ] Track `#ifdef`.
- [ ] Track `#ifndef`.
- [ ] Track `#if`.
- [ ] Track `#elif`.
- [ ] Track `#else`.
- [ ] Track `#endif`.
- [ ] Add branch condition sets to parsed external declarations.
- [ ] Support optional `macro_defines` for active-branch selection.
- [ ] Implement a tiny safe evaluator for simple `defined(NAME)`, `&&`, `||`,
      `!`, `0`, and `1`.
- [ ] Mark declarations that depend on unresolved macros.
- [ ] Store macro-dependency metadata in C parser models.
- [ ] Store preprocessing mode metadata in `CFile`.
- [ ] Store preprocessor configuration metadata such as macro defines and
      include dirs.
- [ ] Do not implement general macro expansion.
- [ ] Do not expand token-paste or stringify macros.
- [ ] Do not attempt recursive compiler-compatible macro expansion inside
      x2py.
- [ ] Add tests for include collection.
- [ ] Add tests for object-like macro collection.
- [ ] Add tests for function-like macro diagnostics.
- [ ] Add tests for conditional branch tracking.
- [ ] Add tests for selected active branches.
- [ ] Add tests for duplicate declarations in mutually exclusive branches.

### Compiler-Assisted Preprocessing Tasks

- [ ] Design a preprocessed-input mode for `.i` files.
- [ ] Design an optional compiler invocation mode for `cc -E` or `clang -E`.
- [ ] Preserve `#line` markers from compiler-preprocessed input.
- [ ] Map diagnostics from preprocessed declarations back to original files.
- [ ] Mark preprocessed declarations with origin metadata.
- [ ] Store the preprocessor command/configuration in `CFile` or `CProject`.
- [ ] Store original and preprocessed source paths when both exist.
- [ ] Add tests for parsing a simple `.i` file.
- [ ] Add tests for `#line` source mapping.
- [ ] Add tests that macro-generated declarations are parseable only when they
      appear in preprocessed input.

### Phase 4 Definition Of Done

- [ ] Lexer/preprocessor preserves source locations.
- [ ] Includes and macros are collected as metadata.
- [ ] Conditional branch tracking exists.
- [ ] No arbitrary macro expansion is attempted.
- [ ] Compiler-assisted preprocessing has a documented design path for
      macro-heavy APIs.
- [ ] Tests cover comments, continuations, directives, and branch selection.

### Phase 4 Risks And Open Questions

- [ ] Decide whether to tokenize fully now or keep logical records until
      declarator parsing requires tokens.
- [ ] Decide whether system headers are recorded only or optionally searched.
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

- [ ] Parse storage class `typedef`.
- [ ] Parse storage class `extern`.
- [ ] Parse storage class `static`.
- [ ] Parse storage class `register`.
- [ ] Parse storage class `_Thread_local`.
- [ ] Parse qualifier `const`.
- [ ] Parse qualifier `restrict`.
- [ ] Parse qualifier `volatile`.
- [ ] Parse qualifier `_Atomic` as basic metadata.
- [ ] Parse `void`.
- [ ] Parse `char`.
- [ ] Parse `signed char`.
- [ ] Parse `unsigned char`.
- [ ] Parse `short`.
- [ ] Parse `short int`.
- [ ] Parse `unsigned short`.
- [ ] Parse `int`.
- [ ] Parse `unsigned`.
- [ ] Parse `unsigned int`.
- [ ] Parse `long`.
- [ ] Parse `long int`.
- [ ] Parse `unsigned long`.
- [ ] Parse `long long`.
- [ ] Parse `unsigned long long`.
- [ ] Parse `float`.
- [ ] Parse `double`.
- [ ] Parse `long double`.
- [ ] Parse `_Bool`.
- [ ] Parse `_Complex` as deferred or supported with explicit tests.
- [ ] Parse `struct name`.
- [ ] Parse `union name`.
- [ ] Parse `enum name`.
- [ ] Parse typedef-name references.
- [ ] Preserve original declaration specifier text.
- [ ] Diagnose unknown specifier sequences.

### Declarator Tasks

- [ ] Parse identifier declarators.
- [ ] Parse pointer declarators.
- [ ] Parse pointer qualifiers.
- [ ] Parse array declarators.
- [ ] Parse multidimensional array declarators.
- [ ] Parse static array parameter qualifiers, for example `int a[static 4]`.
- [ ] Parse parenthesized declarators.
- [ ] Parse function declarators.
- [ ] Parse function pointer declarators.
- [ ] Parse abstract declarators where needed for unnamed parameters.
- [ ] Parse multiple declarators in one declaration.
- [ ] Keep declarator entity order stable.
- [ ] Preserve original declarator source text.
- [ ] Add source locations for each declared entity.
- [ ] Reject or diagnose unsupported declarator forms explicitly.

### Shared Declaration Backend Tasks

- [ ] Implement a helper analogous to `_helper_parse_declaration_line`.
- [ ] Feed procedure parameters through the same declaration backend.
- [ ] Feed function return types through the same declaration backend.
- [ ] Feed struct/union fields through the same declaration backend.
- [ ] Feed typedefs through the same declaration backend.
- [ ] Feed global variables/constants through the same declaration backend.
- [ ] Apply declaration specifiers to declarator-derived type layers.
- [ ] Normalize C type spelling into `CTypeRef`.
- [ ] Preserve typedef references before project resolution.
- [ ] Add tests for each declaration role.
- [ ] Add tests for declarations with multiple variables.
- [ ] Add tests for declarations with initializers.
- [ ] Add tests that local executable statements are not parsed as declarations.

### Phase 5 Definition Of Done

- [ ] Shared declaration/declarator parser exists.
- [ ] It is used by all declaration roles available so far.
- [ ] Primitive, pointer, array, typedef-name, and tag references have tests.
- [ ] Unsupported declaration-shaped input raises `CParseError` or structured
      diagnostics.

### Phase 5 Risks And Open Questions

- [ ] Function pointer parsing is complex; decide which forms are supported in
      extraction and which only produce diagnostics.
- [ ] Typedef-name recognition may require project/type context; decide how to
      represent unresolved names before Phase 8.

## Phase 6: Function Parsing

Branch target:

- `c-parser/phase-6-functions`

Scope:

- Function prototypes and definitions.
- Signature extraction.
- Function body skipping by balanced brace slicing.

### Function Prototype Tasks

- [ ] Classify top-level declarations ending with `;` as possible prototypes.
- [ ] Parse return type through declaration/declarator backend.
- [ ] Parse function name.
- [ ] Parse ordered parameter list.
- [ ] Preserve parameter names.
- [ ] Preserve unnamed parameter types when legal.
- [ ] Parse `void` parameter list as zero parameters.
- [ ] Parse variadic marker `...`.
- [ ] Mark `is_variadic`.
- [ ] Parse pointer parameters.
- [ ] Parse array parameters.
- [ ] Parse function pointer parameters.
- [ ] Parse `const` parameters.
- [ ] Parse `restrict` parameters.
- [ ] Parse `volatile` parameters.
- [ ] Parse storage class `extern`.
- [ ] Parse storage class `static`.
- [ ] Add source locations.
- [ ] Add tests for simple prototypes.
- [ ] Add tests for no-argument prototypes.
- [ ] Add tests for `void` arguments.
- [ ] Add tests for pointer and array parameters.
- [ ] Add tests for const pointer variants.
- [ ] Add tests for variadic prototypes.
- [ ] Add tests for function pointer parameters.

### Function Definition Tasks

- [ ] Classify top-level declarator followed by `{` as function definition.
- [ ] Parse signature from the definition header.
- [ ] Preserve `is_definition=True`.
- [ ] Preserve body source span.
- [ ] Skip body contents for wrapper metadata.
- [ ] Balance braces while respecting strings, chars, and comments.
- [ ] Ignore local declarations for exported signatures in v1.
- [ ] Reject or diagnose K&R style function definitions initially.
- [ ] Add tests for simple definitions.
- [ ] Add tests for nested braces in function body.
- [ ] Add tests for strings containing braces.
- [ ] Add tests for K&R unsupported diagnostics.

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

### Phase 6 Definition Of Done

- [ ] Basic C function signatures parse from `.h` and `.c`.
- [ ] Function bodies are skipped safely.
- [ ] Variadic and function pointer cases are represented and diagnosed.
- [ ] CLI human and JSON output show functions.
- [ ] Readiness reports no-functions only when appropriate.

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

- [ ] Parse named `struct name { ... };`.
- [ ] Parse forward declaration `struct name;`.
- [ ] Parse anonymous `struct { ... }`.
- [ ] Parse typedef anonymous struct `typedef struct { ... } name;`.
- [ ] Parse typedef named struct `typedef struct tag name;`.
- [ ] Parse fields with shared declaration backend.
- [ ] Parse pointer fields.
- [ ] Parse array fields.
- [ ] Parse nested anonymous structs as unsupported or metadata.
- [ ] Parse bitfields as metadata with readiness limitations.
- [ ] Preserve field order.
- [ ] Preserve source locations.
- [ ] Mark incomplete structs.
- [ ] Add tests for named structs.
- [ ] Add tests for forward declarations.
- [ ] Add tests for typedef structs.
- [ ] Add tests for pointer fields.
- [ ] Add tests for array fields.
- [ ] Add tests for bitfield diagnostics.

### Union Tasks

- [ ] Parse named unions.
- [ ] Parse forward union declarations.
- [ ] Parse anonymous unions.
- [ ] Parse typedef unions.
- [ ] Parse union fields with shared declaration backend.
- [ ] Mark union fields distinctly from struct fields.
- [ ] Add readiness diagnostics for by-value unions if unsafe.
- [ ] Add tests for named unions.
- [ ] Add tests for typedef unions.
- [ ] Add tests for union readiness.

### Enum Tasks

- [ ] Parse named enums.
- [ ] Parse anonymous enums.
- [ ] Parse typedef enums.
- [ ] Parse enumerator names.
- [ ] Parse explicit enumerator values.
- [ ] Preserve symbolic enumerator values.
- [ ] Safely fold simple integer expressions.
- [ ] Preserve expression text when folding is unsafe.
- [ ] Add tests for plain enums.
- [ ] Add tests for explicit values.
- [ ] Add tests for expression values.
- [ ] Add tests for typedef enums.

### Typedef Tasks

- [ ] Parse primitive typedefs.
- [ ] Parse pointer typedefs.
- [ ] Parse array typedefs.
- [ ] Parse function pointer typedefs.
- [ ] Parse struct/union/enum typedefs.
- [ ] Preserve alias chains before resolution.
- [ ] Detect duplicate typedefs in same scope.
- [ ] Add tests for typedef chains.
- [ ] Add tests for opaque handle typedefs.
- [ ] Add tests for function pointer typedef diagnostics.

### Phase 7 Definition Of Done

- [ ] C composite and typedef models are populated from basic fixtures.
- [ ] Shared declaration backend handles fields and typedefs.
- [ ] Incomplete/anonymous/bitfield cases are represented or diagnosed.
- [ ] JSON goldens cover composite type schema.
- [ ] Docs list supported and unsupported composite forms.

### Phase 7 Risks And Open Questions

- [ ] Decide when anonymous structs should become generated internal names.
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

- [ ] Discover `.c` files in C mode.
- [ ] Discover `.h` files in C mode.
- [ ] Decide whether `.i` is included now or later.
- [ ] Keep Fortran directory scanning unchanged.
- [ ] Support explicit file lists.
- [ ] Support directory recursion only in explicit C mode.
- [ ] Preserve deterministic file ordering.
- [ ] Add tests for file discovery.

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

- [ ] Index functions by name and file.
- [ ] Index typedefs by name.
- [ ] Index struct tags by tag namespace.
- [ ] Index union tags by tag namespace.
- [ ] Index enum tags by tag namespace.
- [ ] Index enum constants in ordinary identifier namespace.
- [ ] Index macros/constants separately.
- [ ] Detect duplicate definitions.
- [ ] Distinguish compatible redeclarations from conflicts.
- [ ] Add tests for duplicate handling.

### Type Resolution Tasks

- [ ] Resolve typedef chains.
- [ ] Detect typedef cycles.
- [ ] Resolve struct tag references.
- [ ] Resolve union tag references.
- [ ] Resolve enum tag references.
- [ ] Resolve opaque pointer typedefs.
- [ ] Preserve unresolved references for readiness diagnostics.
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
- [ ] Missing project context becomes readiness diagnostics.
- [ ] Tests cover directory and file-list parsing.

### Phase 8 Risks And Open Questions

- [ ] Decide whether project parsing should parse all included system headers
      when found.
- [ ] Decide how to handle generated headers.
- [ ] Decide whether include graph should be path-keyed, module-keyed, or both.

## Phase 9: Wrap-Readiness Diagnostics

Branch target:

- `c-parser/phase-9-readiness`

Scope:

- Actionable readiness diagnostics.
- File-level and unit-level blockers.

### Readiness Schema Tasks

- [ ] Define stable C readiness dictionary keys.
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
- [ ] Assign include/macro/global blockers to file units when no narrower owner
      exists.
- [ ] Use qualified names where available.
- [ ] Avoid per-unit ready flags; keep readiness file-level like Fortran.
- [ ] Add tests for every blocker family.
- [ ] Add CLI readiness formatting tests.

### Phase 9 Definition Of Done

- [ ] Readiness output is stable in JSON and human CLI.
- [ ] Diagnostics identify exactly which units block wrapping.
- [ ] Common unsupported C constructs produce actionable messages.
- [ ] Docs list readiness codes and examples.
- [ ] Tests cover readiness families.

### Phase 9 Risks And Open Questions

- [ ] Decide which pointer cases are blockers versus warnings.
- [ ] Decide how readiness should treat opaque handles.
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
      and callback hook fields.
- [ ] Keep callback hook fields modeled in `c_parser/models.py`, with
      wrap-readiness requiring explicit user `.pyi` callback policy metadata
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
- [ ] Run CLI tests.
- [ ] Run golden fixture tests.
- [ ] Confirm Fortran tests still pass.
- [ ] Audit JSON schema stability.
- [ ] Audit error diagnostic stability.
- [ ] Audit docs for implemented behavior.
- [ ] Remove stale skeleton wording where implementation has matured.
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
- [ ] CLI, JSON, readiness, semantic IR, and `.pyi` workflows are tested.
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
