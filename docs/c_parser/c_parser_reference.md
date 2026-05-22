# C Parser Reference

Status: partial parser reference with raw directive metadata. The `c_parser`
package and explicit C CLI parse path exist, raw includes/simple macros are
recorded, and a first grammar-shaped subset parses simple declarations,
typedefs, globals, function prototypes, and function-definition headers with
start/end locations.

This document is the future home for the C parser user and developer reference.
It should evolve into the C equivalent of `fortran_parser.md` as implementation
lands on `c-parser/main`.

## Purpose

The C parser frontend will be a wrapper-oriented source extraction system for
x2py. It should extract enough stable semantic information from C sources and
headers to help create or update the semantic interface layer.

The implementation must be grammar-style: lex and slice source into C grammar
regions, visit declarations and scopes recursively, reuse shared declarator/type
parsing helpers, and store typed model objects. It must not be implemented as a
giant regex parser, a whole-file scanner, or a compiler-wrapper-only frontend.

It is not intended to be:

- a compiler-grade C frontend
- a full C preprocessor
- a replacement for semantic `.pyi` interfaces
- a libclang-only wrapper
- a C++ parser
- a complete ABI generator

## Planned Source Coverage

Initial source forms:

- `.c`
- `.h`

Possible later source form:

- `.i` preprocessed C input

Project input should accept explicit files and directories. Directory scanning
must be explicit C mode at first to avoid changing Fortran CLI behavior.

## Current Status

Implemented:

- `c_parser` package
- typed C parser models for partial parse reports and raw metadata
- `CParser`, `parse_c_file`, and `parse_c_project`
- `CParseError` with compiler-style diagnostic formatting
- explicit `x2py --language c --parse` output
- C JSON partial output and `--out` behavior
- rejection of C `--semantics`, `--pyi`, and `--wrap-readiness`
- raw lexer records with comment stripping, line-continuation folding, and
  lightweight token source locations
- top-level source splitting that tracks braces, parentheses, brackets, and
  string/character literals
- raw `#include` collection for quoted and system includes
- simple object-like `#define` macro collection
- function-like macro metadata with unsupported diagnostics
- raw `#undef` directive provenance in macro metadata
- simple primitive, pointer, array, and qualifier type extraction
- simple global variable and `typedef` extraction
- simple function prototype extraction
- prototype-style metadata distinguishing `int f(void)` from `int f()`
- simple function-definition signature extraction with body skipping
- start/end locations for function definitions, from the signature start
  through the closing brace
- unsupported K&R function-definition diagnostics
- C fixture inputs under `tests/data/c/general/` plus C fixture directory
  scaffolding for errors, corpus, and scientific APIs

Placeholder only:

- recursive declarator models for parenthesized pointer/array distinctions
- function pointer declarators and callback metadata
- structs, unions, enums, and complex typedef parsing
- project include graph and cross-file type resolution
- preprocessed-input parsing with `#line`/linemarker source mapping
- macro-expanded declaration parsing from preprocessed input
- semantic readiness, semantic IR conversion, and `.pyi` generation

## Planned Supported C Subset

The initial supported subset should focus on stable wrapper-relevant APIs:

- function prototypes
- function definitions with extractable signatures
- primitive C scalar types
- pointers
- arrays in parameters and fields
- `const`, `restrict`, and `volatile` qualifiers
- `static` and `extern` storage classes where wrapper-relevant
- `struct` definitions
- `union` definitions
- `enum` definitions and enumerators
- `typedef` declarations
- simple global constants
- simple object-like numeric and string macros
- include dependency tracking
- cross-file typedef and tag resolution within parsed project files

## Initial Unsupported Subset

The initial C parser should explicitly report or defer:

- full compiler-grade C parsing
- full preprocessor compatibility
- arbitrary macro expansion
- token pasting and stringification
- macro-generated declarations
- complex conditional compilation evaluation
- all compiler extensions
- arbitrary GCC extensions
- arbitrary MSVC extensions
- C++ parsing
- K&R style function definitions
- full ABI generation
- guaranteed struct layout computation
- full bitfield ABI interpretation
- inline assembly
- `_Generic` semantic evaluation
- complex `_Atomic` behavior
- arbitrary attributes before fixture-driven support exists

## Planned Preprocessing Policy

The C parser should be preprocessor-aware, but it should not become a partial
C preprocessor. Partial macro support is risky in C because macros can define
function names, type names, attributes, calling conventions, parameter lists,
and whole declarations. The parser must not infer a public API from unexpanded
macro-shaped declarations.

Raw-source mode means source normalization plus directive metadata:

- strip comments and fold backslash-newline continuations while preserving
  source locations
- record `#include` directives as structured include dependencies
- record simple object-like `#define` directives as macro metadata
- record `#undef` directives as macro provenance
- record function-like macros as metadata with unsupported/deferred diagnostics
- parse only declarations that are already visible as ordinary C without macro
  expansion
- do not select active conditional branches from `#if`/`#ifdef` in raw mode
- do not expand macros, token pasting, stringification, or macro-generated
  declarations

Compiler-assisted preprocessing is the required path when macros affect the
declaration text that the C parser needs to understand. Use preprocessed input
when macros define or alter function names, return types, parameter types,
declarators, attributes, storage classes, calling conventions, visibility
annotations, or conditional API selection. x2py may later accept `.i` files or
invoke a configured compiler preprocessor such as `cc -E` or `clang -E`.

Preprocessed mode must preserve line mapping. That means the parser reads
compiler-preprocessed text, including `#line`/linemarker directives, and maps
every parsed declaration, source location, and diagnostic back to the original
`.h` or `.c` file and line number where possible. Without this mapping, errors
and JSON source locations would point at a generated `.i` file or temporary
preprocessor stream instead of the user's source.

This means macro-heavy APIs are still in scope. The boundary is that x2py v1
should not implement recursive, compiler-compatible macro expansion
internally; it should consume compiler-preprocessed output with preserved
origin metadata.

## Planned Public API

Target module-level entrypoints:

```python
from c_parser import parse_c_file, parse_c_project
```

Implemented signatures:

```python
parse_c_file(
    source_or_path,
    filename=None,
    macro_defines=None,
    include_dirs=None,
    preprocessing="raw",
    encoding="utf-8",
)

parse_c_project(
    files,
    include_dirs=None,
    macro_defines=None,
    preprocessing="raw",
    encoding="utf-8",
)

```

These return typed parser models analogous to the Fortran parser API. The
current partial phase can populate `functions`, `typedefs`, `globals`,
`includes`, `macros`, and metadata `diagnostics`. Composite-type lists such as
`structs`, `unions`, and `enums` remain empty until their dedicated parser
phase lands. Functions include `prototype_style`, currently `"prototype"` for
typed or explicit `void` parameter lists and `"unspecified"` for empty
parameter lists such as `int f()`. Function definitions do not store
executable body text; they include direct `start` and `end` locations.
Re-export from `x2py` is still deferred; users should import from `c_parser`.

`macro_defines` is reserved for future compiler-assisted preprocessing
configuration. It must not mean that raw mode evaluates C preprocessor
conditionals or expands macros internally.

The parser itself should stay parse-only. If the C frontend later gains
wrappability assessment, that should live in the semantic layer after C parser
models are converted to semantic IR or edited `.pyi` policy is loaded, matching
the current Fortran and `.pyi` readiness boundary.

## Planned CLI Usage

Initial explicit mode:

```bash
x2py path/to/api.h --language c --parse
x2py path/to/api.h --language c --parse --json
x2py path/to/api.h --language c --parse --out report.json
```

Optional alias, not implemented:

```bash
x2py path/to/api.h --parse-c
```

Auto-detection should come later, after the frontend is stable.

## Planned JSON Output

Per-file shape:

```text
{
  "<path>": {
    "filename": "<path>",
    "language": "c",
    "parser_status": "partial",
    "preprocessing": "raw",
    "functions": [
      {
        "name": "run",
        "return_type": {"base": "int", "...": "..."},
        "parameters": [],
        "storage": [],
        "specifiers": [],
        "variadic": false,
        "is_definition": false,
        "prototype_style": "prototype",
        "source_location": {"filename": "<path>", "line": 1, "...": "..."},
        "start": {"filename": "<path>", "line": 1, "...": "..."},
        "end": null
      }
    ],
    "structs": [],
    "unions": [],
    "enums": [],
    "typedefs": [],
    "globals": [],
    "macros": [],
    "includes": [],
    "diagnostics": []
  }
}
```

JSON compatibility rules:

- prefer additive schema changes
- include source locations for populated include, macro, and diagnostic models
- preserve unknown or unresolved information rather than dropping it silently
- keep model fields stable enough for golden fixture testing
- document every intentional schema break

## Planned Readiness Boundary

The parser should not assess wrappability.

Any future C readiness rules should be implemented after the parser output is
converted to semantic IR, or after an edited `.pyi` file provides the missing
policy. That keeps the C parser aligned with the current project rule that
readiness is a semantic concern, not a parser concern.

For C callback-bearing APIs, the parser should still preserve enough source
facts to let later semantic work decide what is safe:

- callback signature
- callback direction: native-to-Python, Python-to-native, or both
- lifetime: call-only, stored by native, or released by a specific API
- associated context/userdata parameter
- nullability rules
- non-default calling convention
- threading or async behavior
- ownership of callback and context memory
- release/unregistration API
- exception/error policy for Python callback failures

Those facts should be stored in parser models, but not turned into a parser-side
`wrappable` report.

## Error Handling

The parser defines `CParseError` with:

- `filename`
- `line_number`
- `column`
- `source_line`
- `base_message`
- `code`
- internal parser raise location for debug mode
- `format_diagnostic(color=False, debug=None)`

The CLI should print compiler-style diagnostics without tracebacks by default.
The parser has the error type and formatter. Raw directive collection can emit
non-fatal metadata diagnostics, such as unresolved local includes or
function-like macros that were recorded but not expanded. K&R-style function
definitions now raise `CParseError` because the current function parser only
models prototype-style declarations and definitions. The current grammar subset
is otherwise intentionally tolerant for unsupported declaration forms; more hard
syntax errors should be added only with focused tests.

## Planned Testing Workflow

Test families should mirror the Fortran parser:

- focused lexer tests
- declaration-specifier tests
- declarator parser tests
- function prototype tests
- function definition tests
- struct/union/enum tests
- typedef tests
- macro/constant tests
- include/project tests
- semantic readiness tests once C semantic conversion exists
- CLI tests
- semantic conversion tests
- `.pyi` generation/parser tests
- fixture/golden parser tests
- error fixture/golden tests
- corpus parse-only tests

The C test area now contains both unskipped partial-parser/raw-metadata tests
and skipped roadmap tests under `tests/parser/c/`. The active tests cover
public entrypoints, empty model serialization, CLI discovery, JSON/output-file
behavior, unsupported C stages, comment stripping, line-continuation folding,
top-level splitting, include collection, simple macro collection, macro-shaped
declaration deferral, raw conditional branch non-selection, simple declarations,
globals, typedefs, and simple function prototypes/definitions, including
function-definition start/end locations. The broader roadmap tests remain skipped
until their matching implementation branches land. Future implementation
branches should unskip only the tests for the capability they implement, then
merge those branches back into `c-parser/main`.

Fixture layout should be separate from Fortran:

```text
tests/data/c/
  general/
  errors/parser/
  corpus/
  scientific/

tests/parser/c/
  fixtures/
  errors/
  generate_c_parser_goldens.py
```

The first real-world corpus target should be cJSON, pinned to an exact release
or commit with license and source provenance. cJSON is small enough for early
stabilization while still covering typedef structs, recursive pointers, public
macro declaration wrappers, constants, `const char *` APIs, `size_t`, and
callback hook fields.

## Planned Documentation Set

The C parser documentation lives under:

```text
docs/c_parser/
```

Current documents:

- `c_parser_reference.md`
- `c_parser_architecture.md`
- `c_parser_cli_workflow.md`
- `c_parser_implementation_checklist.md`
- `c_parser_main_merge_guard.md`

Documentation update rule: every C parser implementation change must update
all affected files under `docs/c_parser/` in the same change. This includes
changes to parser behavior, public API, models, CLI output, tests, fixture
workflow, semantic conversion, semantic readiness, or `.pyi` output. Do not
wait for a separate documentation request before updating these docs.
