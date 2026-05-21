# C Parser Reference

Status: skeleton reference. The `c_parser` package and explicit C CLI parse
path exist, but no real C declarations are parsed yet.

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

- `c_parser` package skeleton
- typed empty C parser models
- `CParser`, `parse_c_file`, and `parse_c_project`
- `CParseError` with compiler-style diagnostic formatting
- explicit `x2py --language c --parse` skeleton output
- C JSON skeleton output and `--out` behavior
- rejection of C `--semantics`, `--pyi`, and `--wrap-readiness`

Placeholder only:

- function extraction
- declarations and declarators
- structs, unions, enums, and typedef parsing
- include and macro collection
- project include graph and cross-file type resolution
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

The C parser should have clear preprocessing modes instead of trying to become
a full C preprocessor.

Raw-source mode should parse declarations that are visible without arbitrary
macro expansion, collect includes, collect simple object-like constants, track
conditional branches, and preserve macro-dependent declarations as parser model
metadata.

Compiler-assisted preprocessing should be the practical path for macro-heavy
APIs. x2py may later accept `.i` files or invoke a configured compiler
preprocessor such as `cc -E` or `clang -E`. In that mode, the parser should
preserve `#line` mapping, record the preprocessor command/configuration, and
mark declarations that came from preprocessed input.

This means macro-heavy APIs are not out of scope. The boundary is that x2py v1
should not implement recursive, compiler-compatible macro expansion internally.

## Planned Public API

Target module-level entrypoints:

```python
from c_parser import parse_c_file, parse_c_project
```

Implemented skeleton signatures:

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

These return typed parser models analogous to the Fortran parser API. During
the skeleton phase they return empty C file/project models. Re-export from
`x2py` is still deferred; users should import from `c_parser`.

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

Optional alias, not implemented in the skeleton:

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
    "parser_status": "skeleton",
    "preprocessing": "raw",
    "functions": [],
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
- include source locations once parser models exist
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
The skeleton has the error type and formatter, but real syntax diagnostics are
not produced yet because grammar parsing is still deferred.

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

The C test area now contains both unskipped skeleton tests and skipped roadmap
tests under `tests/parser/c/`. The skeleton tests cover public entrypoints,
empty model serialization, CLI discovery, JSON/output-file behavior, and
unsupported C stages. The broader roadmap tests remain skipped until their
matching implementation branches land. Future implementation branches should
unskip only the tests for the capability they implement, then merge those
branches back into `c-parser/main`.

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
