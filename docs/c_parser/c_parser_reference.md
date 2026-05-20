# C Parser Reference

Status: planning reference. The C parser is not implemented yet.

This document is the future home for the C parser user and developer reference.
It should evolve into the C equivalent of `fortran_parser.md` as implementation
lands on `c-parser/main`.

## Purpose

The C parser frontend will be a wrapper-oriented source extraction system for
x2py. It should extract enough stable semantic information from C sources and
headers to help create or update the semantic interface layer.

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
from c_parser import parse_c_file, parse_c_project, assess_c_wrap_readiness
```

Expected signatures:

```python
parse_c_file(
    source_or_path,
    filename=None,
    macro_defines=None,
    include_dirs=None,
    encoding="utf-8",
)

parse_c_project(
    files,
    include_dirs=None,
    macro_defines=None,
    encoding="utf-8",
)

assess_c_wrap_readiness(
    code,
    filename=None,
    include_dirs=None,
    macro_defines=None,
)
```

These should return typed parser models and dictionaries analogous to the
Fortran parser API. Re-export from `x2py` should wait until the API is tested
and documented.

## Planned CLI Usage

Initial explicit mode:

```bash
x2py path/to/api.h --language c --parse
x2py path/to/api.h --language c --parse --json
x2py path/to/api.h --language c --parse --wrap-readiness
```

Optional alias:

```bash
x2py path/to/api.h --parse-c
```

Auto-detection should come later, after the frontend is stable.

## Planned JSON Output

Per-file shape:

```text
{
  "<path>": {
    "language": "c",
    "parser_status": "implemented|partial|skeleton",
    "functions": [],
    "structs": [],
    "unions": [],
    "enums": [],
    "typedefs": [],
    "globals": [],
    "macros": [],
    "includes": [],
    "diagnostics": [],
    "wrap_readiness": {}
  }
}
```

JSON compatibility rules:

- prefer additive schema changes
- include source locations once parser models exist
- preserve unknown or unresolved information rather than dropping it silently
- keep model fields stable enough for golden fixture testing
- document every intentional schema break

## Planned Readiness Diagnostics

Readiness should answer whether the parsed C API is safe enough for x2py to
wrap automatically or semi-automatically.

Expected readiness categories:

- unsupported constructs
- parse errors
- unresolved includes
- unresolved typedefs
- unresolved struct/union/enum tags
- incomplete public types
- macro-dependent declarations
- variadic functions
- function pointers and callbacks
- pointer ownership ambiguity
- pointer mutability ambiguity
- array extent ambiguity
- unsupported compiler extensions
- no functions found

The top-level readiness report should keep a file-level `wrappable` boolean
and unit-scoped blockers, following the Fortran parser pattern.

Function pointers and callbacks should be parsed into C models when possible.
They should not be marked wrap-ready until the user supplies enough `.pyi`
policy to explain how wrapper generation should handle them.

The required user policy should make these facts explicit:

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

## Planned Error Handling

The parser should define `CParseError` with:

- `filename`
- `line_number`
- `column`
- `source_line`
- `base_message`
- `code`
- internal parser raise location for debug mode
- `format_diagnostic(color=False, debug=False)`

The CLI should print compiler-style diagnostics without tracebacks by default.

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
- readiness tests
- CLI tests
- semantic conversion tests
- `.pyi` generation/parser tests
- fixture/golden parser tests
- error fixture/golden tests
- corpus parse-only tests

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

## Planned Documentation Set

The C parser documentation lives under:

```text
docs/c_parser/
```

Current planning documents:

- `c_parser_reference.md`
- `c_parser_architecture.md`
- `c_parser_cli_workflow.md`
- `c_parser_implementation_checklist.md`

Future implementation should update these docs in the same change whenever C
parser behavior, public API, CLI output, fixture workflow, semantic conversion,
or `.pyi` output changes.
