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
- Keep parser output parse-only. Wrap-readiness is assessed after conversion to
  semantic IR, either from parsed Fortran or from an edited `.pyi` interface.
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
- Internal procedures inside `contains` blocks are structurally sliced, then
  their declarations and bodies are ignored when parsing a parent routine
  signature.
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
- Symbolic kind/length references are preserved and resolved where the parser
  has enough local, module, or project context. Remaining syntactically valid
  symbols are carried forward for semantic conversion/readiness instead of
  becoming parser JSON readiness fields.

### 2.4 Compile-time symbol and expression resolution

- Local `parameter` constants collected inside procedure scope.  
- Module-scope `parameter` constants collected in module specification part.  
- `use <module>, only: ...` symbol import maps collected and attached to
  procedures/modules. Each explicit import records the imported `source` name
  and optional local `target` name so renamed imports survive JSON,
  semantic conversion, and `.pyi` printing.  
- Signature kind expressions resolved transitively (symbol -> symbol -> value),
  including renamed imports from parsed modules. Safely evaluable arithmetic
  parameter chains are folded to their final integer kind; compiler-dependent
  intrinsics such as `selected_real_kind(...)` remain as resolved expressions.  
- Procedure-local parameter expressions can be folded into argument shapes
  during procedure finalization. Module-level and `use`-associated parameters
  used in procedure argument shapes remain symbolic in the signature while
  still being visible to downstream semantic conversion/readiness.
- Module/program variable parameter values, character lengths, and shapes are
  resolved through the same cached compile-time resolver where safe.
- The resolver caches symbol and expression results per scope and evaluates a
  restricted set of initialization intrinsics (`abs`, `max`, `min`, `mod`,
  `len`, `len_trim`, `iachar`, `int`) plus arithmetic and comparisons.
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

### 2.9 Parser/semantic readiness boundary

- The parser no longer owns wrap-readiness.
- `FortranParser` does not expose `visit_wrap_readiness(...)`.
- `fortran_parser.parser` does not expose `assess_wrap_readiness(...)`.
- Parser JSON does not contain `wrap_readiness`, `wrappable`,
  `wrappability_blockers`, `unit_blockers`, `unsupported_constructs`, or
  `unknown_argument_types` readiness payloads.
- Parser responsibility ends at producing typed parse models and parse-stage
  diagnostics such as `FortranParseError`.
- Readiness is a semantic feature:
  - For Fortran input, `x2py --wrap-readiness` parses the source, converts the
    parsed model to semantic IR, and assesses that semantic interface.
  - For `.pyi` input, `x2py --wrap-readiness` parses the edited stub directly to
    semantic IR and assesses that interface.
  - The edited `.pyi` is the source of truth when the user supplies missing
    wrapper information such as imported types, compile-time constants, or
    callback signatures.
- Combining `x2py --parse --wrap-readiness --json` keeps stage payloads
  separate:
  - top-level `parse` contains parse-only JSON
  - top-level `wrap_readiness` contains semantic readiness JSON
- Combining `x2py --semantics --wrap-readiness` attaches the readiness payload to
  the semantic report because both payloads are semantic-stage artifacts.

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
- CLI JSON output emits per-file parser buckets for signatures, types, modules,
  submodules, programs, and block data.  
- CLI human output prints tree-like structure grouped by file/module/procedure.  
- Parser JSON serializes explicit `use` symbols as objects containing
  `source` and `target`. Bare imports still use an empty list.
- Semantic IR imports use structured `SemanticImport` / `SemanticImportItem`
  entries when a Fortran `use` has an explicit symbol list; bare imports remain
  plain module names for compatibility.
- The `.pyi` printer emits structured imports as `from module import name` or
  `from module import source as target`; the `.pyi` parser accepts the same
  syntax and restores the semantic import mapping.
- Fortran `parameter` values are represented in semantic IR with the existing
  `Constant` constraint. The `.pyi` printer renders those as `Final[...]`, and
  the `.pyi` parser maps `Final[...]` back to the `Constant` constraint.
- Parser JSON serializes both parameter `value` and `symbolic_value`. `value`
  is literal/evaluated only; compiler-specific or unresolved expressions keep
  `value: null` and preserve the original expression in `symbolic_value`.
- Semantic readiness JSON is emitted by `x2py --wrap-readiness`, not by
  `fortran_parser` parse JSON.

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
- executable parser-internals tutorial in
  `tests/parser/test_parser_developer_tutorial.py`
- ignoring local vars in external signatures
- external callback declarations (including typed `real, external :: f`) under `implicit none`
- ignoring internal procedures in `contains`
- local parameter propagation into argument kinds
- compile-time shape expression evaluation helpers
- shape symbol collection helpers
- parse-stage diagnostics and unsupported declaration handling

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
- Semantic wrap-readiness message fixtures are separate from parser goldens:
  - `python tests/semantics/generate_wrap_readiness_fixtures.py`
  - generated output: `tests/semantics/fixtures/wrap_readiness_messages.json`
  - covered corpus: `general`, `blas`, `lapack`, and `scifortran`

### 4.5 CLI tests (`tests/parser/test_cli.py`)

Validates command-line behavior for:
- path expansion
- human-readable output
- JSON output
- JSON file writing
- module/free-procedure name collision handling
- parse-error diagnostics without tracebacks by default
- developer traceback opt-in through `--debug`, its compatibility alias
  `--debug-traceback`, and `FORTRAN_PARSER_DEBUG=1`
- default ANSI color for diagnostics, with `--no-color` and `NO_COLOR=1` opt-out
- parser JSON remains parse-only and does not include semantic readiness fields

Semantic readiness CLI behavior is tested in
`tests/semantics/test_semantic_wrap_readiness.py`, including `.pyi` input,
Fortran input, combined `--parse --wrap-readiness` human output, combined JSON
stage separation, and `--semantics --wrap-readiness`.

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
2. Source-unit slicer that preserves original line numbers and returns direct
   children for each scope.  
3. Grammar-region splitter for `header`, specification part, execution part,
   and `contains`.  
4. Unit visitors for modules, submodules, programs, procedures, derived types,
   interfaces, and block data.  
5. Shared declaration parser for variables, procedure arguments/results, and
   derived-type fields, with scope-specific storage handled separately.  
6. Procedure signature parser (headers, args, attributes, result handling).  
7. Module/package parser with import/use tracking.  
8. Composite type parser (fields, inheritance, bound methods/generics).  
9. Interface/contract block parser.  
10. Symbol resolver for local and cross-file compile-time constants.  
11. Project namespace parser with dependency ordering.  
12. Semantic readiness validator outside the parser, fed by semantic IR from
    parsed source or `.pyi`.  
13. CLI with tree output + JSON output + file emission.  
14. Unit tests per feature + fixture/golden regression suite + golden
    regeneration script.  


### 6.1 Parser control-flow example

Use this as the mental model when changing `fortran_parser/parser.py`: parsing
is recursive over source units, and each unit is handled by the same grammar
shape before grammar-specific exceptions are applied.

```fortran
module m
  type :: state
    integer :: n
  end type state
contains
  subroutine work(x)
    real, intent(inout) :: x(:)
  end subroutine work
end module m
```

The control flow is:

1. `visit_file` preprocesses the source, validates recognizable headers, and
   asks `_helper_slice_child_units` for direct file-scope units.
2. The slicer returns one `_SourceUnit(kind="module", name="m")` whose `lines`
   are exactly the module substring and whose line numbers are the original
   file line numbers.
3. `visit_source_unit` dispatches the slice to `visit_module_unit`.
4. `visit_module_unit` builds a module `_ParserScope`, splits the module into
   `header`, specification part, execution part, and `contains` using
   `_helper_split_unit_parts`, then calls `_helper_visit_spec_part` on the
   module specification lines.
5. The module visitor slices its own direct children. The `type :: state` slice
   goes to `visit_derived_type_unit`; the contained `subroutine work` slice goes
   to `visit_procedure_unit`.
6. `visit_derived_type_unit` and `visit_procedure_unit` repeat the same pattern:
   build a scope, split the unit, visit the relevant specification part, and
   push declarations into that scope.

The grammar shape is the design rule:

- every sliced source unit has a header and a specification part
- procedures and programs can also have an execution part
- modules, submodules, programs, procedures, and derived types can have a
  `contains` part, but visitors decide whether children in that region matter
  for wrapping
- block data is specification-only
- interfaces use the same child-slicing mechanism for procedure declarations

That means new parser behavior should usually be implemented by extending the
grammar profile, unit splitter, or shared specification/declaration helpers,
not by adding a new whole-file scan.

Declaration parsing is deliberately shared. Module variables, program/block
data variables, procedure arguments/results, and derived-type fields all call
`_helper_parse_declaration_line`, then `_helper_push_declaration_to_scope`.
The small spec-line visitors only cover grammar exceptions: module visibility
and `use`, procedure `implicit`/`import`/`external`/local parameters, and
derived-type `sequence`/`private`/type-bound declarations.

Sibling validation happens at each recursive slicing level. Duplicate
same-level units are errors, but identical names in different scopes are
allowed; for example, `module a; type :: state ...` and
`module b; type :: state ...` parse as two separate type scopes.
End-name validation is strict for module/submodule/program/interface/derived
type scopes. Procedure end-name labels are tolerated when the end statement is
the right procedure kind, because some real third-party fixtures contain
copy/paste labels that do not match the opening procedure name; duplicate
procedure names are still checked at the sibling scope.

### 6.2 Executable developer tutorial

`tests/parser/test_parser_developer_tutorial.py` is a runnable tutorial for the
private parser flow. It intentionally uses `FortranParser` internals and ends
with asserts, so maintainers can read it as sample code and pytest can keep it
honest.

The tutorial demonstrates this sequence:

```python
parser = FortranParser()
lines, root_scope, top_units = parser._helper_prepare_source_units(source, filename)
module_parts = parser._helper_split_unit_parts(
    top_units[0],
    parser._helper_unit_grammar("module"),
    filename=filename,
)
module = parser.visit_source_unit(top_units[0], parent_scope=root_scope, filename=filename)
module_scope = parser._helper_scope_for_model("module", module, parent=root_scope)
child_units = parser._helper_slice_child_units(
    top_units[0].lines[1:-1],
    parent_scope=module_scope,
    filename=filename,
)
```

Use that test when changing the recursive slicer or the small `visit_*_unit`
methods: it documents how file parsing becomes unit parsing, how unit parsing
becomes child-unit parsing, and how the active scope is passed into shared
declaration helpers.

## 7) Scope handling and valued-variable mechanics (explicit)

These behaviors are easy to miss, but they are core to correctness and are
implemented today:

- **Procedure argument scope isolation**: declarations only apply to symbols
  belonging to the current procedure header argument/result symbol table;
  unrelated locals do not overwrite signature arguments.
- **Module specification scope tracking**: module `parameter` collection is
  restricted to the module specification part and stops at `contains`, avoiding
  leakage from executable regions.
- **Module parameter references in contained procedure shapes**: a contained
  procedure argument such as `real :: x(n)` may refer to a module-level
  parameter `n`. The signature keeps the shape token symbolic (`"n"`) while
  downstream semantic readiness can use the semantic compile-time metadata. This
  protects module-level parameters from being mistaken for undeclared procedure
  locals.
- **Interface scope tracking**: procedures parsed inside `interface ... end
  interface` are represented separately and flagged as interface procedures.
  Interface-local argument declarations do not conflict with host declarations;
  callback dummies referenced by interface headers are typed as `procedure`.
- **Interface import tracking**: `import :: symbol` inside an interface
  procedure is treated as procedure metadata and emitted as an `import(symbol)`
  signature attribute, rather than as a module variable declaration.
- **Internal procedure scope protection**: nested procedures in a host
  `contains` block are structurally sliced to check their unit boundaries and
  placement, but their declarations and bodies are not parsed or merged into
  the host routine signature.
- **Name-reuse safety across scopes**: fixtures/tests cover same identifier
  reuse in separate host/internal/type scopes to ensure no cross-scope symbol
  pollution.
- **Preprocessor branch-aware duplicate checks**: duplicate procedure names are
  allowed in mutually exclusive `#if/#ifdef` branches but still raise when two
  same-name procedures are active in overlapping branch conditions.
- **Valued variables map**: compile-time constants are preserved as
  `FortranVariable(name, value, symbolic_value)` records in signature metadata.
  `value` stores only a literal/evaluated value when the parser can determine
  one; otherwise it is `None`. `symbolic_value` keeps the original parameter
  expression for validation, downstream diagnostics, and JSON consumers.
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
- Added valued-variable support and tests, including separate symbolic and
  resolved parameter values.
- Refined CLI tree output (omit empty/internal sections; stable module
  procedure grouping).
- Added tests/fixtures for same-name reuse across different scopes.
- Added parser public API coverage for less common module/import forms and
  preserved `use` rename source/target mappings through JSON, semantic IR, and
  `.pyi` import aliases.
- Refactored `FortranParser.visit_file` onto recursive source-unit slicing:
  file parsing now dispatches direct units to small `visit_*_unit` methods,
  each unit works on its own source substring, and shared declaration helpers
  push parsed symbols into the active scope.
- Collapsed old full-method parser helpers into visitor methods and kept
  helpers focused on reusable grammar pieces: slicing, scope setup,
  specification-part handling, declaration parsing, and validation.
- Refreshed parser goldens for the grammar-style parser. Procedure-internal
  subprograms are no longer exported as file/module procedures; local
  interfaces remain available for callback typing and interface metadata.

## 9) Pull-request maintenance policy for this reference

To keep this document useful as an implementation transfer artifact, pull
requests should update `docs/fortran/parser_implementation_reference.md` whenever parser
behavior, parser coverage, parser fixtures/goldens, or parser validation flow
meaningfully changes.

A CI guard in `.github/workflows/parser-reference-guard.yml` enforces this on pull requests by
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
unless `docs/fortran/parser_implementation_reference.md` is updated in the PR
diff.

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
  - Wrapper generation/readiness should decide from semantic IR or `.pyi`
    whether a parsed feature is safe to wrap. Parser errors should be about
    unsupported grammar/metadata, not about a filename implying an older or newer
    language standard.
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
  - Symbolic kind names from intrinsic modules must be made visible by a `use`
    statement; names such as `c_double`, `real64`, or aliases introduced through
    `only: local => remote` are not hard-coded as globally available.
  - Unresolved but syntactically valid kind symbols are not parser errors by
    themselves; semantic conversion/readiness decides whether the final interface
    has enough compile-time information.
  - Semantic conversion is stricter than parsing: a parsed intrinsic
    `base_type`/`kind` pair must map to a concrete semantic type, otherwise
    conversion raises instead of emitting `Unknown`. Generated `.pyi` output and
    `.pyi` parsing also reject `Unknown` type annotations.
  - When the missing type information depends on compiler-specific constants,
    `collect_semantic_compile_time_requirements` reports the unknown expression
    and semantic conversion accepts `compile_time_values` to specialize the IR.
- **Post-scope validation (hard error):**
  - After parsing each module, derived type, or procedure scope, a validation pass checks that all declared variables/fields/arguments have a known (non-`"unknown"`) base type; failures raise `FortranParseError`.
  - Under `implicit none`, missing declarations are treated as hard errors. For functions:
    - if the header uses an explicit `result(name)`, an undeclared result raises an "Unknown datatype for function result ..." error for that result symbol
    - otherwise the result is implicitly the function name and the usual "has no type declaration (implicit none is active)" wording is used
- **Design intent:**
  - The parser is intentionally strict about unknown declarations and internal
    metadata consistency, but permissive about mixed-era Fortran syntax that can
    be parsed unambiguously.
  - "Unsupported but recognized" constructs may be carried far enough for
    semantic readiness or `.pyi` completion to decide wrappability. Unknown
    datatype syntax should crash early.
- **Preprocessor-conditional duplicate procedures (guarded allowance):**
  - The parser does **not** run a full C preprocessor stage before parsing.
  - While slicing source units, simple directive structure is tracked for
    `#ifdef`, `#ifndef`, `#elif`, `#else`, and `#endif` to model
    mutually-exclusive branches.
  - `visit_file(..., macro_defines=...)` can provide macro decisions; inactive conditional branches are skipped before unit parsing so the active code path is selected. The module-level `parse_fortran_file(...)` convenience function delegates to this visitor.
    - accepted forms: `set[str]` or `dict[str, int|bool|str]`
    - dictionary values are truthy/falsey (`0`, `False`, `"0"`, `"false"` treated as undefined/disabled)
  - Basic `#if` expressions are supported for branch selection (`defined(X)`, `!`, `&&`, `||`, parentheses, `0`/`1`).
  - Duplicate procedure-name checks in a module/global scope are evaluated
    against same-level sliced units and this branch context:
    - if two same-name procedure headers are reachable in an overlapping branch context, raise `FortranParseError` (duplicate procedure name).
    - if they are only present in mutually-exclusive branches of the same conditional group, allow both signatures.
  - This is a structural exclusivity model (branch groups), not semantic evaluation of macro expressions. In other words, branch mutual exclusivity is honored without requiring expression truth evaluation.

`FortranParseError` is a subclass of `ValueError` and carries structured location metadata:
- `filename` — source file path (if provided)
- `line_number` — 1-based line number in the original source where the error was detected
- `source_line` — the original (pre-preprocessed) source line text
- `base_message` — the stable error message without source/location context
- `code` — stable diagnostic category identifier; current parser errors default
  to `PARSE001`, while grammar rejection uses `PARSE_INVALID_SYNTAX`
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

The numeric suffix in a code such as `PARSE001` identifies an error category
for tests, tools, and documentation. It is not a line number, an occurrence
counter, or an exit status. The shared registry is
[`docs/diagnostic_codes.md`](../diagnostic_codes.md).

CLI contract:
- End-user parse failures are caught, rendered to `stderr` with
  `format_diagnostic(...)`, and return exit status `1`; they do not print Python
  tracebacks by default.
- CLI diagnostics request ANSI color by default when available.
- `--no-color` and `NO_COLOR=1` disable ANSI color in CLI diagnostics.
- `--debug` re-raises `FortranParseError` so Python prints the full traceback
  for parser developers. `--debug-traceback` remains a compatibility alias.
- `FORTRAN_PARSER_DEBUG=1` enables the same traceback/debug behavior without
  changing command-line arguments.

Implementation note: enforce these checks close to lexical declaration handling (source-form check + declaration parse) so behavior is consistent across signatures, types, modules, and interfaces. Preserve the original source line and line number whenever possible so diagnostics can show the Fortran source context rather than only the error text.
