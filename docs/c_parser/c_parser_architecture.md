# C Parser Architecture Plan

Status: partial parser plus raw directive metadata implemented. The `c_parser`
package, typed parser models, public entrypoints, explicit
`x2py --language c --parse` CLI path, raw include/macro/undef/conditional
metadata collection, top-level redeclaration handling, project include/index
reporting, top-level source splitting, and a first simple
declaration/function subset with function-definition start/end locations and
aggregate declarations exist. Declarators are parsed through a recursive
grammar-style path for pointer, array, function, and parenthesized combinations.
The x2py CLI also has a shared C/Fortran preprocessing option surface and can
run an exact compiler/preprocessor executable for C compiler mode. Compiler
and preprocessed C inputs preserve `#line`/GCC linemarker source locations for
parsed declarations and diagnostics. A separate compiler-derived standard-type
probe supplies target ABI facts consumed by C semantic conversion.

This document records the target architecture for the C parser frontend in
x2py. The initial skeleton has grown into a partial parser, and the remaining
sections describe the architecture it should grow into. The design is based on
inspection of the
current Fortran parser, semantic IR conversion layer, `.pyi` parser/printer,
CLI, tests, and fixture workflow.

## Current Implementation Snapshot

Implemented now:

- `c_parser/` package exists and is included in package discovery.
- `c_parser.models` defines JSON-stable parser dataclasses and `CParseError`.
- `c_parser.parser` exposes `CParser`, `parse_c_file`, and `parse_c_project`.
- `x2py` re-exports `parse_c_file` and `parse_c_project`, matching its
  Fortran file/project entrypoint style.
- `c_parser.parser` keeps parser helpers on `CParser`, matching the Fortran
  parser's stateful class structure; module-level functions are limited to
  public entrypoints and small path helpers.
- `c_parser.lexer` strips comments safely, folds backslash-newline logical
  records, exposes lightweight token records, and provides top-level splitting
  helpers that track braces, parentheses, brackets, literals, and
  function-definition end locations.
- `c_parser.preprocessor` records raw `#include` directives, simple object-like
  macros, `#undef` directives, conditional/pragma directive provenance
  including OpenMP declaration pragmas, and unsupported function-like macro
  diagnostics without expanding macros.
- `c_parser.parser` parses variables, typedefs, incomplete `struct`/`union`
  tags, basic struct/union/enum definitions, function prototypes, and
  function-definition signatures while skipping bodies. Declarator handling
  follows the C declarator grammar for pointer prefixes, parenthesized direct
  declarators, and array/function suffixes, including functions returning
  function pointers and arrays of callback pointers. Incomplete tags are
  recorded as `CStruct` or `CUnion` objects with `is_incomplete=True`.
  Declaration types are represented by concrete `CType` subclasses:
  primitives, `CPointer`, `CArray`, `CFunctionType`, and
  `CComposedType`. Aggregate members are `CVariable` objects using that same
  type path and preserve arrays, callback candidates, bit-width text, and
  member-level source locations. Supported flexible final struct members set
  `CArray.is_flexible=True`; invalid flexible-member placement and union use
  produce `C_INVALID_FLEXIBLE_ARRAY_MEMBER` diagnostics. Function signatures
  that use unions by value produce `C_UNION_BY_VALUE` diagnostics while
  pointer-to-union signatures remain parsed normally.
  Inline tag definitions followed by aliases or objects produce concrete
  `CTypedef` or `CVariable` records linked to the aggregate object. Function
  models expose `result_type` and named `parameters`; their derived
  `CFunctionType` is the nameless callable signature. Array and function
  parameter declarations preserve their written `declared_type` and expose
  pointer-adjusted effective `type` values. Declarations prefixed by
  unexpanded object-like macros are deferred as macro dependencies rather than
  misreported as invalid type sequences. Selected unsupported declaration
  forms, including attributes, alignment specifiers,
  C++-shaped declarations, and static assertions, are reported as diagnostics with
  explicit `unit_kind` values. A declarator must be fully consumed before a
  concrete object is returned; unknown suffixes become diagnostics. Primitive
  specifier order is normalized, and invalid combinations such as
  `unsigned float` raise `CParseError` with code `CPARSE003` while a single
  unresolved typedef-like name remains deferred. Definitions preserve direct
  `start` and `end` locations from the signature start through the closing
  brace; and K&R-style function definitions raise focused diagnostics.
- Top-level redeclaration handling merges compatible repeated declarations,
  completes incomplete struct/union tags when a later definition is parsed,
  prefers compatible function or variable definitions over earlier
  declarations, preserves related declaration locations, and reports duplicate
  definitions or incompatible redeclarations as diagnostics. Local declarations
  inside function bodies remain out of scope because bodies are skipped.
- Raw same-name function alternatives in mutually exclusive conditional
  branches retain Fortran-style `condition_set` identity; a project keeps
  ambiguous alternatives in `conditional_function_variants` rather than
  inventing one selected function.
- `c_parser.cli` provides C-specific partial report formatting.
- `x2py.cli` dispatches `--language c --parse` to the C parser path.
- `x2py.c_type_probe` compiles and runs a generated C11 query for
  `size_t`, `uint32_t`, `time_t`, and opaque `FILE` pointer ABI facts,
  preserving compiler/runner/source provenance for semantic conversion. It
  carries target-relevant include, macro, undefine, and compiler-argument flags
  and records the requested project standard as provenance.
- `semantics.c2ir` converts the supported C parser subset into semantic IR,
  including scalar functions, pointer storage contracts, declared arrays,
  structs/opaque structs, enum and numeric macro constants, local typedef
  chains, target standard-type probe facts, and C-specific readiness blockers.
- `--language c --semantics` and `--language c --wrap-readiness` are enabled.
  `--language c --pyi` remains rejected until C `.pyi` emission exists.
- Focused partial CLI/API, declaration/function, diagnostic color, project
  include/index, raw lexer/directive, project golden, error golden, preprocessed
  linemarker remapping, and JSON schema tests are active. Remaining
  parser-suite skips are limited to the pinned corpus roadmap.
- `tests/data/c/` contains general fixtures modeled after the Fortran general
  fixture themes, additional C-specific API shapes, fatal diagnostic inputs,
  and real-world cJSON/jsmn/tinyexpr/linmath/NanoSVG/stb inputs whose partial
  project parse reports are covered by regression goldens.

Deferred:

- full typedef/tag resolution policy beyond basic project-level link-up and
  callback policy metadata, for example conflict diagnostics, active
  semantic wrappability decisions
- compiler attributes and alignment specifiers
- broader compiler-family validation for preprocessing; parsed declarations
  already retain preprocessed origin and mapped source identity
- C `.pyi` output and broader callback/ownership policy

Documentation rule: any future C parser implementation change must update all
affected docs under `docs/c_parser/` in the same change. This applies to model,
parser, CLI, test, fixture, semantic, and `.pyi` changes; documentation updates
should not wait for a separate request.

## Inspected Repository Areas

- `README.md`
- `docs/fortran/fortran_parser.md`
- `docs/fortran/parser_implementation_reference.md`
- `docs/architecture/semantic_multilanguage_wrapper_runtime_architecture.md`
- `docs/semantics/pyi_format.md`
- `fortran_parser/lexer.py`
- `fortran_parser/parser.py`
- `fortran_parser/models.py`
- `fortran_parser/type_resolver.py`
- `fortran_parser/utils.py`
- `fortran_parser/cli.py`
- `x2py/cli.py`
- `x2py/__init__.py`
- `semantics/models.py`
- `semantics/fortran2ir.py`
- `semantics/pyi_printer.py`
- `semantics/pyi_parser.py`
- `tests/parser/test_cli.py`
- `tests/parser/test_fortran_fixture_suite.py`
- `tests/parser/test_fortran_error_fixture_suite.py`
- `tests/parser/test_parser_developer_tutorial.py`
- `tests/parser/c/test_c_parser_developer_tutorial.py`
- `tests/parser/test_parser_public_entrypoints.py`
- `tests/semantics/test_semantic_wrap_readiness.py`
- `tests/parser/test_error_handling.py`
- `tests/semantics/test_fortran2ir.py`
- `tests/semantics/test_semantic_conversion_smoke.py`
- `tests/pyi/test_pyi_to_ir.py`
- `tests/pyi/test_pyi_fixture_suite.py`
- `tests/parser/fortran/generate_fortran_parser_goldens.py`
- `tests/parser/fortran/errors/generate_fortran_parser_error_goldens.py`
- `tests/parser/c/generate_c_parser_goldens.py`
- `tests/parser/c/errors/generate_c_parser_error_goldens.py`
- `tests/semantics/generate_semantic_fixtures.py`
- `tests/pyi/generate_pyi_fixtures.py`
- `tests/_shared/fixture_outputs.py`

## Architectural Observations From The Existing Parser

The Fortran parser is not a compiler frontend. It is a wrapper-oriented
semantic extraction frontend with a bounded language subset. Its important
architectural properties are:

- A lexer/preprocessor stage normalizes source while preserving original line
  numbers and source lines for diagnostics.
- The parser uses recursive source-unit slicing instead of a whole-file scan.
- Each source unit is parsed inside an explicit `_ParserScope`; there is no
  ambient global current module/procedure stack.
- Unit visitors are small and grammar-shaped: file, module, submodule, program,
  procedure, interface, derived type, and block data each receive only their
  own source substring.
- The shared declaration parser is reused for procedure arguments/results,
  module variables, program variables, block data variables, and derived type
  fields.
- Grammar-region splitting separates header, specification, execution, and
  contains regions. Wrapper extraction mostly ignores executable bodies.
- Parser model objects are typed dataclasses with stable JSON-friendly fields.
- Project parsing builds indexes and dependency order from imports/uses.
- Readiness is semantic-layer work, not parser work. The C parser should
  preserve enough source facts for later semantic readiness, but it should not
  expose parser-side `wrappable` reports.
- CLI output has a stable human tree, JSON output, output file behavior,
  no-color support, and debug traceback opt-in.
- Semantic IR conversion is a separate visitor layer. Parser output is a helper
  input, not the source of truth.
- `.pyi` generation and parsing operate over semantic IR, not parser internals.
- Fixture testing combines focused unit tests, parser JSON goldens, error
  goldens, semantic fixtures, `.pyi` fixtures, and corpus parse-only coverage.

The C parser should follow these patterns where they map cleanly to C syntax.
It should not be a giant regex parser, a compiler wrapper, or a libclang-only
dependency architecture.

## Grammar-Style Parser Requirement

The C frontend must be implemented as a grammar-style recursive parser, not as
an unstructured source scanner. The core parser should be shaped around C
grammar regions and reusable visitors:

- translation-unit visitor
- preprocessor directive collector
- declaration visitor
- declarator parser
- initializer skipper/extractor where wrapper-relevant
- function prototype visitor
- function definition visitor that extracts signatures and skips bodies
- struct, union, enum, and typedef visitors
- scoped symbol/type indexes

Regular expressions are acceptable only as narrow helpers inside a grammar
step, such as recognizing an include directive after the preprocessor collector
has isolated the line. They must not become the top-level parsing strategy.

External compiler preprocessing can be used as an optional input source for
macro-expanded views, but the x2py C frontend still needs its own typed parser
models, source-location handling, diagnostics, and project indexes. Invoking a
compiler must not replace the grammar-style parser. The current x2py CLI can
run an exact user-supplied compiler executable through `--preprocess compiler`
and parse the preprocessed stdout through the same C parser. `#line` and
GCC/Clang linemarkers are used to remap parsed locations and diagnostics back
to the original source.

## Package Layout

The implementation lives in a separate package so it does not destabilize the
Fortran parser:

```text
c_parser/
  __init__.py
  __main__.py
  cli.py
  lexer.py
  models.py
  parser.py
  preprocessor.py
  project.py
  type_resolver.py
  utils.py

x2py/
  c_type_probe.py
```

Current and planned responsibilities:

- `c_parser/models.py`
  - Implemented: typed parser models, `CParseError`, compiler-style
    diagnostic rendering, concrete `CType` composition, and JSON-stable
    dataclass serialization, including declared/effective parameter type facts.
  - Planned: resolved symbol links, richer macro/preprocessing provenance,
    and project indexes.
- `c_parser/lexer.py`
  - Implemented: safe comment removal that preserves line mapping, logical
    record folding for backslash-newline, string/character literal awareness,
    lightweight tokens with source locations, preprocessed `#line`/linemarker
    remapping for top-level segments, top-level splitting with block end
    locations, and delimiter splitting aware of nesting and literals.
  - Planned: richer token helpers as extension and initializer-expression
    parsing require them.
- `c_parser/preprocessor.py`
  - Implemented: lightweight raw directive metadata for includes,
    object-like macros, `#undef` directives, function-like macro diagnostics,
    and local include resolution when a matching file is available.
  - Compiler-assisted recipe metadata is persisted by the shared
    `x2py.preprocessing` CLI input path and attached to generated `CFile`
    JSON output.
- `c_parser/parser.py`
  - Implemented: `CParser`, `parse_c_file`, `parse_c_project`,
    translation-unit visiting, declaration/function visitors, grammar-shaped
    recursive declarator parsing, concrete `CType` construction, and aggregate
    member extraction. Helper methods live on `CParser` rather than as broad
    module-level functions. The file now follows the Fortran parser's
    maintainer-facing organization pattern with a module architecture guide,
    public visitors first, sectioned helper groups, and docstrings on parser
    helper methods. Function models record prototype-style versus unspecified
    empty parameter lists, function definitions preserve start/end locations,
    K&R-style definitions are rejected with `CParseError`, and invalid
    primitive-specifier combinations are rejected with `CPARSE003`. Array and
    function parameters preserve `declared_type` while effective `type` uses C
    parameter adjustment. Raw declarations beginning with an object-like macro
    name are retained as macro-dependent diagnostics.
  - Planned: symbol resolution and additional declaration-specifier and
    extension coverage.
- `c_parser/project.py`
  - Compatibility export for project parsing.
  - Project behavior is implemented through `CParser.visit_project`, including
    `.c`/`.h`/`.i` discovery, include graphs, and header/source association.
- `c_parser/type_resolver.py`
  - Resolves tag and typedef references, typedef chains/cycles, and aggregate
    references across parsed project files.
  - Boundary: enum initializer expressions remain source text in the parser;
    any target-aware evaluation belongs to later semantic conversion.
- `c_parser/cli.py`
  - Implemented: report formatting and serialization helpers called by
    `x2py.cli` behind explicit C flags.
  - Planned: richer human output as more C facts are populated.
- `c_parser/utils.py`
  - Placeholder now.
  - Planned: shared helpers that are not parser-state dependent.
- `x2py/c_type_probe.py`
  - Implemented: compiler/target-derived JSON facts for standard-header
    arithmetic aliases and opaque `FILE` pointer ABI information.
  - Boundary: target ABI facts are inputs to future semantics, not declarations
    guessed by raw parser mode or stored as `CFile` syntax facts.

## Public API Shape

The public C API mirrors the Fortran style but remains C-specific:

```python
parse_c_file(source_or_path, filename=None, macro_defines=None, include_dirs=None, preprocessing="raw", encoding="utf-8") -> CFile
parse_c_project(files, include_dirs=None, macro_defines=None, preprocessing="raw", encoding="utf-8") -> CProject
```

`macro_defines` is reserved for future compiler-assisted preprocessing
configuration. It must not cause raw mode to evaluate C preprocessor
conditionals or expand macros inside x2py.

Implemented companion class:

```python
class CParser:
    def visit_file(...): ...
    def visit_project(...): ...
```

These entrypoints are exposed from both `c_parser` and `x2py.__init__`, using
the same top-level file/project invocation pattern already provided for
Fortran. C semantic conversion is exposed separately through
`semantics.c2ir` and top-level `x2py` compatibility helpers.

## Core Model Families

All declared types inherit from `CType`, which stores `qualifiers` and
`source_text`. Type qualifiers are concrete values: `CConst`, `CVolatile`,
`CRestrict`, and `CAtomic`. Both `_Atomic int` and `_Atomic(type)` forms are
parsed; for a composed inner type the atomic qualifier stays on its outermost
component.

The implemented primitive `CType` subclasses are:

- `CVoid`, `CBool`, `CChar`, `CSignedChar`, and `CUnsignedChar`
- `CShort`, `CUnsignedShort`, `CInt`, and `CUnsignedInt`
- `CLong`, `CUnsignedLong`, `CLongLong`, and `CUnsignedLongLong`
- `CFloat`, `CDouble`, and `CLongDouble`
- `CFloatComplex`, `CDoubleComplex`, and `CLongDoubleComplex`

Derived and named `CType` subclasses are:

- `CPointer`, whose qualifiers apply to that pointer component
- `CArray`, with `bound`, `is_static_minimum`, `is_variable_length`, and
  `is_flexible`; supported final flexible struct members are classified now,
  and invalid placement or union use produces a parser diagnostic
- `CFunctionType`, the nameless callable signature with `result_type`,
  `parameter_types`, `is_variadic`, and `prototype_style`
- `CComposedType`, whose `components` are read from the declared name outward
- `CStruct`, `CUnion`, and `CEnum`, which are tag types as well as aggregate
  declaration objects
- `CTypedef`, which represents either a declared alias with its underlying
  `type`, or an unresolved typedef-name use until symbol resolution is added
- `CUnknownType`, retained for type states that cannot yet be modeled; invalid
  primitive-specifier combinations no longer become `CUnknownType`

For example, composition order distinguishes the following declarations:

```python
int *values[4];       # CComposedType([CArray(bound="4"), CPointer(), CInt()])
int (*matrix)[4];     # CComposedType([CPointer(), CArray(bound="4"), CInt()])
int *(*table)[4];     # CComposedType([CPointer(), CArray(bound="4"), CPointer(), CInt()])
```

Declaration objects are separate from the type components:

- `CVariable` has `name`, `type`, `storage`, optional `initializer`, optional
  `bit_width`, source/callback metadata, and related declaration locations.
  Struct and union `members` are also `CVariable` objects with per-member
  locations; there is no separate field class.
- `CFunction` has `name`, `result_type`, named `parameters`, storage and
  function specifiers, `is_variadic`, prototype style, and source/definition
  locations plus related declaration locations. Raw alternative declarations
  can also carry `condition_set` tokens such as `g1:b0`, matching the
  Fortran parser's conditional-sibling identity convention. Its `type`
  property builds the corresponding nameless `CFunctionType`.
- `CParameter` has a source name, written `declared_type`, and effective
  `type`; outer array parameters and direct function parameters adjust to
  pointer `type` values while their source form is retained.
- `CInitializer` preserves initializer source text without claiming evaluation.
- `CStruct` and `CUnion` expose `members` and `is_incomplete`; `CEnum` exposes
  `constants`; `CEnumerator` preserves enumerator name and value text.
- `CTypedef` has its alias name, declared `type`, and related declaration
  locations.
- `CMacro`
  - `name`
  - `value`
  - `function_like`
  - `directive`
  - `source_location`
- `CRawDirective`
  - `directive`
  - `argument`
  - `source_location`
- `CMacroDependency`
  - `name`
  - `context`
  - `source_location`
- `CInclude`
  - `target`
  - `kind`
  - `resolved_path`
  - `source_location`
- `CFile`
  - `filename`
  - `language`
  - `parser_status`
  - `preprocessing`
  - `functions`
  - `structs`
  - `unions`
  - `enums`
  - `typedefs`
  - `variables`
  - `macros`
  - `includes`
  - `raw_directives`
  - `macro_dependencies`
  - `diagnostics`
- `CProject`
  - `files`
  - `functions`
  - `structs`
  - `unions`
  - `enums`
  - `typedefs`
  - `variables`
  - `macros`
  - `includes`
  - `functions_by_file`
  - `enum_constants`
  - `include_graph`
  - `system_includes`
  - `unresolved_includes`
  - `header_source_pairs`
  - `conditional_function_variants`
  - `diagnostics`

Serialization uses `"model"` to identify concrete `CType` nodes; `"type"` is
reserved for semantic type relationships such as `CVariable.type` and
`CTypedef.type`. Concrete qualifier objects serialize using their canonical
spellings, such as `"const"`. Reused aggregate/typedef objects serialize as
references to avoid cycles.

Future parser phases can deepen symbol links, duplicate/conflict diagnostics,
and project diagnostics when the corresponding behavior lands. Additions
should be documented and tested with stable serialization expectations.

## Grammar-Style Parsing Strategy

C does not have Fortran-style modules, but it still has parseable scoped
regions:

- translation unit
- preprocessor directive lines
- external declarations
- function prototypes
- function definitions
- declaration specifier sequences
- declarators
- parameter declaration lists
- struct/union/enum definitions
- compound statement bodies

The C parser parses external declarations by slicing top-level grammar
regions, not by scanning the full file repeatedly. The high-level flow should
be:

1. Normalize source through a C lexer/preprocessor layer.
2. Produce tokens or logical source records with original source locations.
3. Visit the translation unit.
4. Split direct external declarations while balancing parentheses, brackets,
   braces, string literals, and comments.
5. Classify each external declaration:
   - include/preprocessor directive
   - typedef
   - function prototype
   - function definition
   - forward struct declaration or struct/union/enum definition
   - file-scope variable/static const
   - unsupported/macro-dependent declaration
6. Dispatch to a small visitor for that declaration kind.
7. Use a shared declaration-specifier and declarator parser to build type
   references for functions, parameters, members, variables, and typedefs.
8. Ignore executable function bodies except where needed to find the matching
   brace and preserve function start/end locations.

## Declarator-Centered Design

C type syntax is declarator-centered. Declarator parsing stays a first-class
subsystem, not a pile of ad hoc string splitting. The current parser applies
one recursive declarator path to variables, typedefs, function signatures,
parameters, and aggregate members; future work should extend that grammar-shaped
path rather than adding parallel splitting rules.

Layered pieces:

- declaration specifier parser
  - storage classes: `extern`, `static`, `typedef`, `register`, `_Thread_local`
  - qualifiers: `const`, `restrict`, `volatile`, `_Atomic`
  - atomic type specifier: `_Atomic(type)`
  - primitive base: `void`, `char`, `short`, `int`, `long`, `float`, `double`,
    `_Bool`, `_Complex`
  - signedness: `signed`, `unsigned`
  - tags: `struct`, `union`, `enum`
  - typedef-name references
- declarator parser
  - identifier extraction
  - pointer chains
  - arrays
  - function parameters
  - parenthesized declarators
  - function pointers
  - anonymous abstract declarators where needed
- entity applier
  - convert one declaration specifier plus one declarator into a typed model
  - reuse this for function returns, parameters, members, variables, and typedefs

This is the C equivalent of the Fortran parser's shared declaration backend.

## Preprocessing Strategy

The C frontend must be preprocessor-aware without trying to be a full C
preprocessor in v1.

The practical rule is: x2py should not own preprocessor correctness. Partial
macro expansion is especially dangerous in C because macros can participate in
function names, type names, declarators, attributes, calling conventions,
visibility annotations, and entire declarations. Raw mode must therefore avoid
guessing what macro-expanded declarations mean. Macro-heavy APIs are still in
scope, but the supported path for those APIs is compiler-assisted preprocessing
with line mapping. The parser supports raw-source mode,
compiler/preprocessed-input mode, and direct `.i` input; declarations parsed
from preprocessed source carry `origin="preprocessed"`. For compiler streams
produced by the shared x2py CLI, `CFile` JSON records a
`preprocessing_recipe`: compiler executable, final argv,
include dirs, defines, undefines, standard, working directory, and optional
selected `compile_commands.json` entry.

Raw-source mode target:

- Strip comments safely while preserving line numbers.
- Fold backslash-newline continuations.
- Record `#include` directives as structured include dependencies.
- Record `#define` object-like macros for simple constants.
- Record `#undef` directives as macro provenance.
- Record function-like macros as unsupported or deferred metadata.
- Record conditional directive presence as metadata only when needed for
  provenance.
- Preserve same-name function declarations from mutually exclusive raw
  conditional branches as separate `condition_set` variants; do not select an
  active branch in raw mode.
- Parse ordinary declarations only when they are visible without macro
  expansion.
- Mark function-like wrappers and object-like declaration-prefix regions as
  unsupported/deferred rather than treating them as parsed declarations.
- Do not select active branches from `#if`/`#ifdef` in raw mode.

Compiler-assisted preprocessing target:

- Accept a preprocessed stream from a configured compiler command such as
  `gcc-13 -E`, `clang-18 -E`, or an absolute compiler path. Users normally pass
  `.h`/`.c` inputs and have x2py generate the stream; direct `.i` input is
  accepted when a generated stream already exists.
- Use a shared x2py CLI option shape for C and Fortran:
  `--preprocess compiler`, `--compiler`, `-I`, `-D`, `-U`, `--std`, and
  `--compiler-arg`.
- Require exact compiler executables in direct compiler mode, for example
  `gcc-13`, `clang-18`, `/usr/bin/gfortran-12`, or
  `/opt/intel/oneapi/compiler/latest/bin/ifx`, instead of silently choosing a
  generic default.
- Accept C `compile_commands.json` entries for project builds and strip
  compile-only flags before adding `-E`.
- Preserve `#line` marker information so diagnostics can map preprocessed
  declarations back to original files.
- Treat `#line`/linemarker directives as the source of truth for
  `source_location` fields after preprocessing.
- Store the original input path and exact invocation recipe for
  CLI-generated compiler input.
- Mark declarations discovered only after preprocessing with
  `origin="preprocessed"` or equivalent model metadata.
- Record the macro definitions/include directories/preprocessor command that
  produced the parse, because different `-D` and `-I` settings can expose
  different public APIs.
- Treat function-like macros as metadata in raw mode, but allow their expanded
  declarations to be parsed when they appear in compiler-preprocessed input.
- Require preprocessed input whenever public declarations depend on macros for
  names, types, declarators, attributes, storage classes, calling conventions,
  visibility annotations, or active conditional branches.

Initial non-goal:

- Do not implement arbitrary macro expansion.
- Do not attempt token-paste/stringify semantics.
- Do not implement recursive compiler-compatible macro semantics inside x2py.
- Do not require libclang as the only way to understand headers.

## Project Parsing Strategy

C project parsing should account for include graphs instead of Fortran `use`
graphs.

Current behavior:

- `parse_c_project` accepts mappings, explicit paths, and directories.
- Directory mode discovers `.c`, `.h`, and `.i` files.
- Returned `CProject` objects contain `CFile` parser models with raw include,
  macro, metadata diagnostics, and supported declarations populated per file.
- Basic project-level indexes are populated for parsed functions, typedefs,
  variables, macros, includes, functions by file, and enum constants.
- Quoted local includes are recorded in an `include_graph`; system includes
  are recorded separately. Unresolved quoted includes remain diagnostics
  rather than hard failures, and include cycles are represented as graph edges
  without recursive traversal.
- Included local or system files are never recursively parsed, even when a
  local path can be resolved. The parser reads only explicit mapping/file
  inputs or supported files below an explicit directory, matching the
  Fortran policy of recording imports/includes without loading them.
- Generated headers and direct `.i` inputs follow that explicit-input rule;
  compiler linemarkers record origins rather than introducing project files.
- Project and include-graph keys are input/path keys. There is no C module-key
  namespace; a graph edge uses a parsed project-file key when one matches and
  otherwise retains its external path/target fact.
- Likely header/source pairs are reported by matching stems and direct source
  includes.
- Basic cross-file typedef and struct/union/enum tag references are linked to
  project index objects after all files are parsed. Original type spelling is
  preserved in the model `source_text`.
- Basic duplicate/conflict analysis is populated; broader policy remains
  fixture-driven work.

Planned behavior after project-resolution phases:

- Deepen include graph behavior where normalized paths are ambiguous.
- Deepen duplicate/conflict diagnostics.
- Track duplicate symbols by C namespace:
  - ordinary identifiers
  - typedef names
  - struct/union/enum tags
  - labels are not wrapper-relevant and should not enter the public index
- Keep project resolution tolerant enough to parse partial projects, while
  parser diagnostics and metadata preserve missing dependencies for later
  semantic readiness.

## Readiness Boundary

The parser should not compute wrappability. That responsibility belongs to the
semantic layer, after parser models are converted into semantic IR or after an
edited `.pyi` file supplies the missing policy.

What the parser should still preserve is the source information needed for that
later stage:

- unresolved include references
- unresolved typedef/tag references
- macro-dependent declarations
- variadic functions
- pointer ownership and mutability ambiguity
- incomplete public types
- callback and function-pointer structure
- unsupported extension markers

These should become parser diagnostics or parser metadata, not a parser-side
`wrappable` report or a parser JSON readiness payload.

## Parser-First Model Policy

For the current planning horizon, the C parser should store C-specific facts in
`c_parser/models.py`. It currently stores function-pointer signatures,
callback-candidate markers, type qualifiers, raw include dependencies, and
unresolved typedef/tag uses. Preprocessed input records declaration origin and
mapped source identity; CLI-generated compiler input also records its
preprocessing recipe. Later phases should add ownership policy and deepen
resolved symbol/conflict handling. Standard-header aliases whose representation
matters to semantic conversion are supplied separately by `x2py.c_type_probe`,
with exact compiler, generated source, and runner provenance.

Semantic IR conversion is deliberately later work. When that phase starts, the
IR model may need extensions for C pointer ownership, unsigned integer types,
callbacks, opaque handles, function pointer policies, and preprocessing-origin
metadata. The parser should not wait for those IR decisions before preserving
the source facts it can extract.

## Semantic IR Mapping

The semantic layer is the source of truth. The C parser should only help create
or update semantic modules.

Planned mapping:

- C file or header group -> `SemanticModule`
- C function -> `SemanticFunction`
- C parameter -> `SemanticArgument`
- C primitive -> `SemanticType`
- C pointer -> constraints and ownership metadata
- C array -> subscription shape notation such as `T[n]`, order metadata such as
  `ORDER_C`, and pointer/extent metadata
- `const` -> read-only ownership/constraint metadata
- `restrict` -> aliasing metadata
- structs/unions -> `SemanticClass` or named opaque semantic type
- enums -> constants or a future semantic enum representation
- typedefs -> semantic aliases or metadata, depending on IR support at the
  time of implementation
- standard-header aliases (`size_t`, `uint32_t`, `time_t`) -> semantic
  integer/real types using compiler-derived width and signedness facts
- `FILE *` -> opaque handle/pointer semantics using pointer ABI facts rather
  than importing library-private layout
- macros/constants -> `SemanticArgument` module variables with `Constant`
  where safe

Pointer ownership and lifetime should be conservative. Ambiguous pointers
should be represented with diagnostics and metadata rather than guessed as safe
Python APIs.

## `.pyi` Integration

Generated `.pyi` stubs for C should come after parser models and semantic IR
conversion are stable. Readiness, if added for C, should follow the semantic
layer pattern already used by the project.

Likely stub patterns:

- plain scalar functions:
  - `def f(x: Int32) -> Float64: ...`
- pointer arguments:
  - use storage/calling contracts such as `Ptr(...)`, `Const(...)`, writable
    metadata, and explicit extent metadata only after the IR supports them
    cleanly
- arrays:
  - `Annotated[Float64[n], ORDER_C]`
- opaque handles:
  - classes or named semantic types with ownership constraints
- structs:
  - `class struct_name: ...` when field layout is useful and stable
- callbacks:
  - generated stubs should include callback declarations only after user policy
    fields are designed and supported
- constants:
  - `Final[...]`

The existing `.pyi` parser already supports `Final`, `private`, `native_call`,
imports, classes, functions, shape subscriptions, storage contracts, metadata,
and native projection entries. C-specific work should extend the semantic model
intentionally before changing `.pyi` syntax.

For function pointers and callbacks, parser extraction and later wrappability
are separate decisions. The parser should extract the function pointer type into
C models whenever possible. If a callback-bearing API later becomes wrappable,
that should be because the user supplied enough `.pyi` policy for the semantic
layer to make the decision. The policy needs to identify:

- the callback signature, including argument and return semantic types
- whether native calls Python, Python passes a callback to native, or both
- whether the callback is used only during the call or stored by native code
- which context/userdata parameter, often `void *`, is paired with it
- whether `NULL` is allowed for the callback and/or context
- the calling convention when it is not the platform default
- whether invocation is synchronous, asynchronous, same-thread, or arbitrary
  native-thread
- who owns callback and context memory
- how and when a stored callback is released
- what should happen if the Python callback raises

Until those fields exist and are supplied, any future readiness layer should
report an explicit callback policy blocker rather than pretending the function
is safely wrappable.
