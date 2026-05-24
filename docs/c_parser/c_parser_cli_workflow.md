# C Parser CLI Workflow Plan

Status: C parser partial subset plus raw directive metadata implemented. The
CLI command shape exists and parse reports can include raw includes, simple
macros, `#undef` provenance, metadata diagnostics, variables, typedefs,
aggregate declarations, function prototypes, prototype-style metadata, and
function-definition signatures with start/end locations. Declarator output can
represent parenthesized pointer/array precedence through concrete
`CComposedType` components and nameless `CFunctionType` signatures.

This document records the implemented C parse command shape, output schema,
and diagnostic contract, plus deferred CLI behavior.

## Current Status

Implemented commands:

```bash
python -m x2py path/to/api.h --language c --parse
python -m x2py path/to/api.h --language c --parse --json
python -m x2py path/to/api.h --language c --parse --out report.json
```

The C parser accepts explicit `.c` and `.h` files, plus directories in explicit
C mode. Directory scanning in C mode only collects `.c` and `.h` files.
Auto-detection is deferred, so omitting `--language` keeps the current Fortran
behavior.

The C parser output differs from Fortran parser output by using C-specific
top-level sections: `functions`, `structs`, `unions`, `enums`, `typedefs`,
`variables`, `macros`, `includes`, and `diagnostics`. The current partial parser
can populate `functions`, `typedefs`, `variables`, `structs`, `unions`, and
`enums` in the supported subset. Typedefs, variables, parameters, and aggregate
members can include concrete composed types for pointer/array/function forms,
including function pointers, functions returning function pointers, and
legal final flexible struct members marked with `is_flexible=True`. Raw
`includes`, `macros`, and metadata `diagnostics` can also be
populated. The object class distinguishes declarations (`CFunction`,
`CVariable`, `CTypedef`, `CStruct`, `CUnion`, or `CEnum`), and incomplete tag
declarations set `is_incomplete=True`.
Known unsupported declaration forms such as declaration attributes, alignment
specifiers, `_Atomic(type)`, nested aggregate member definitions, and static assertions are
reported in diagnostics with explicit `unit_kind` values; unconsumed declarator
suffixes are diagnosed instead of silently omitted. Invalid flexible array
member placement and flexible union members produce
`C_INVALID_FLEXIBLE_ARRAY_MEMBER` error diagnostics at the field location. The parser reports
`parser_status: "partial"`. C parse diagnostics, currently including
unsupported K&R-style function definitions and invalid primitive-specifier
combinations such as `unsigned float`, honor `--no-color` and `NO_COLOR=1`.
Function definitions do not store executable body text; they preserve a
direct `start` location and `end` location from the signature start through the
closing brace.

Unsupported C stages:

```bash
python -m x2py path/to/api.h --language c --semantics
python -m x2py path/to/api.h --language c --pyi
python -m x2py path/to/api.h --language c --wrap-readiness
```

These commands return clear argparse errors until C semantic IR conversion and
`.pyi` generation are implemented. Fortran-only parse display flags such as
`--show-vars` and `--print-limit` are rejected in C mode.

## Current CLI Baseline

The current `x2py` CLI is Fortran-oriented:

```bash
python -m x2py <path ...> --parse
python -m x2py <path ...> --parse --json
python -m x2py <path ...> --wrap-readiness
python -m x2py <path ...> --semantics
python -m x2py <path ...> --semantics --wrap-readiness
python -m x2py <path ...> --pyi
```

Important current behaviors to preserve:

- Stage flags are explicit: `--parse`, `--semantics`, `--pyi`.
- `--out` writes stage output and suppresses stdout.
- `--json` prints JSON for the selected stage output.
- `--wrap-readiness` is semantic readiness. It can be requested alone for
  Fortran or `.pyi` inputs, or combined with other stages.
- Parser JSON remains parse-only. Combined `--parse --wrap-readiness --json`
  keeps parse and readiness payloads in separate top-level sections.
- Parse diagnostics are compiler-style and go to stderr.
- Python tracebacks are hidden by default.
- `--debug-traceback` or parser debug env vars re-raise parse errors.
- Diagnostics use ANSI color by default unless `--no-color` or `NO_COLOR=1`
  disables it.
- Human parse output is a stable tree.
- JSON parse output is a stable per-file object keyed by input path.

The C CLI must integrate without breaking any of these Fortran behaviors.

## Command Shape Recommendation

Strong initial preference:

```bash
x2py <path ...> --language c --parse
```

Rationale:

- It is explicit.
- It scales to future language frontends.
- It avoids surprising users by auto-detecting mixed-language directories too
  early.
- It lets Fortran remain the default during the long C parser stabilization
  period.

Optional short alias, not implemented:

```bash
x2py <path ...> --parse-c
```

The short alias is convenient, but should be secondary. If added, it should be
implemented as a strict alias for `--language c --parse`.

Auto-detection should be later:

```bash
x2py <path ...> --parse
```

Auto-detection should wait until C parser behavior is mature enough to handle
mixed source trees predictably. Until then, `--parse` without `--language`
should keep existing Fortran behavior.

## Flags And Deferred Options

Initial flags:

```text
--language {fortran,c}
--parse
--json
--out [PATH]
--no-color
--debug-traceback
```

Current C behavior also accepts `--no-color`. `CParseError` supports
compiler-style diagnostic formatting and the `C_PARSER_DEBUG` environment
variable. The current grammar subset is tolerant for recoverable unsupported
declaration forms, but invalid primitive-specifier combinations raise
`CPARSE003`; unresolved single typedef-name uses are deferred until type
resolution can determine whether a declaration exists.

C-specific flags to add only when needed:

```text
--include-dir PATH
--show-macros
--show-includes
--print-limit N
```

Potential later flags:

```text
--auto-language
--project
--header-mode
--source-mode
--preprocessed
--preprocess-command PATH_OR_COMMAND
--define NAME[=VALUE]
--undef NAME
```

`--define` and `--undef` should belong to compiler-assisted preprocessing, not
to raw parser-side macro evaluation. Raw C mode records directives and parses
ordinary visible declarations only; it does not select `#if` branches or expand
macros.

## Current Partial Behavior

Phase 1 implemented CLI structure before a real declaration parser existed.
The command shape remains stable as the parser starts populating model fields:

```bash
x2py include/example.h --language c --parse
```

Human output:

```text
File: include/example.h
  Language: c
  Functions: 1
  Structs: 0
  Unions: 0
  Enums: 0
  Typedefs: 0
  Variables: 0
  Macros: 0
  Includes: 0
  Diagnostics: 0
  Parser status: partial
```

JSON output for a file without raw directives:

```json
{
  "include/example.h": {
    "filename": "include/example.h",
    "language": "c",
    "parser_status": "partial",
    "preprocessing": "raw",
    "functions": [
      {
        "name": "run",
        "result_type": {
          "model": "CInt",
          "qualifiers": [],
          "source_text": "int"
        },
        "parameters": [],
        "storage": [],
        "specifiers": [],
        "is_variadic": false,
        "is_definition": false,
        "prototype_style": "prototype",
        "source_location": {"filename": "include/example.h", "line": 1, "...": "..."},
        "start": {"filename": "include/example.h", "line": 1, "...": "..."},
        "end": null
      }
    ],
    "structs": [],
    "unions": [],
    "enums": [],
    "typedefs": [],
    "variables": [],
    "macros": [],
    "includes": [],
    "diagnostics": []
  }
}
```

The parser should not claim C files are wrappable. If C readiness is added
later, it should follow the semantics-owned readiness boundary used elsewhere
in x2py, not become parser JSON.

For raw directives, the same JSON shape is used, but `includes`, `macros`, and
`diagnostics` may contain populated model dictionaries. Function-like macros
are recorded as macro metadata and also produce a non-fatal
`C_UNSUPPORTED_FUNCTION_LIKE_MACRO` diagnostic. Local quoted includes are
resolved relative to the current file when possible; unresolved local includes
produce `C_UNRESOLVED_INCLUDE` diagnostics instead of hard failures.

Raw mode must not claim support for macro-generated declarations. If macros
affect function names, types, parameters, attributes, storage classes, calling
conventions, visibility annotations, or active conditional branches, the user
should provide compiler-preprocessed input later through a `.i` file or an
explicit preprocessor command. That preprocessed path must preserve
`#line`/linemarker mappings so parser diagnostics and JSON `source_location`
fields still point back to the original `.h` or `.c` file.

## JSON Parse Schema

The C parse JSON is per-file and does not reuse Fortran key names when the
concepts differ. Current top-level per-file keys:

```text
language
filename
parser_status
preprocessing
functions
structs
unions
enums
typedefs
variables
macros
includes
diagnostics
```

Declaration/directive records include `source_location`; diagnostics use
`location`. Concrete type components preserve `source_text` rather than their
own source-location object:

```text
source_location: {
  filename: str | null,
  line: int | null,
  column: int | null,
  source_line: str | null
}

location: {
  filename: str | null,
  line: int | null,
  column: int | null,
  source_line: str | null
}
```

Concrete `CType` values serialize with a `"model"` discriminator, for example
`{"model": "CInt", "qualifiers": [], "source_text": "int"}`. The `"type"`
key is reserved for a semantic relationship such as a `CVariable` or
`CTypedef` pointing to its declared type. Qualifier objects serialize as
canonical spelling strings such as `"const"`. Aggregate/typedef object reuse
emits a reference rather than a recursive JSON cycle.

## Human Tree Output

The current human tree is the count-only report shown above. A later expanded
tree could mirror the Fortran parser style:

Initial mature output shape:

```text
File: src/api.c
  Includes: 2
    - api.h
    - stddef.h
  Functions: 2
    - int add(int a, int b)
    - void scale(double *x, size_t n)
  Structs: 1
    - struct vector (members=2)
  Typedefs: 1
    - vector_t -> struct vector
  Macros: 1
    - MAX_DIM = 16
```

Future semantic readiness output should be described in the semantic-layer
documentation, not in the parser CLI workflow.

## Diagnostics Behavior

Fatal C syntax errors use `CParseError` with the same user experience as
`FortranParseError`:

```text
src/api.h:12:5: error[CPARSE001]: Unsupported declaration.
   |
12 |     __attribute__((vector_size(16))) float v;
   |     ^
```

Default CLI behavior:

- print the formatted diagnostic to stderr
- exit with status code `1`
- do not show Python traceback
- colorize when color is enabled

Unsupported but recoverable declarations and raw preprocessor limitations are
stored as non-fatal `CDiagnostic` entries in the parse report instead.
Invalid primitive-specifier combinations that are independent of symbol
resolution are fatal:

```text
src/api.h:12:1: error[CPARSE003]: Invalid type specifier sequence 'unsigned float'.
12 | unsigned float value;
   | ^
```

Debug behavior:

- `--debug-traceback` re-raises the error
- `C_PARSER_DEBUG=1` re-raises C parser errors
- `FORTRAN_PARSER_DEBUG` should not control C behavior
- a generic `X2PY_DEBUG=1` may be considered later

Color behavior:

- `--no-color` disables ANSI diagnostics
- `NO_COLOR=1` disables ANSI diagnostics
- Windows color behavior can follow the existing `colorama` pattern

## CLI Test Expectations

The active CLI/parser tests cover the current partial subset:

- Existing Fortran CLI tests still pass unchanged.
- `python -m x2py --help` lists `--language`.
- `python -m x2py <file.c> --language c --parse` is accepted.
- `python -m x2py <file.c> --parse-c` is not implemented.
- `--language c --parse --json` emits stable partial-parser JSON with raw
  include/macro metadata and supported declarations when present.
- `--language c --parse --out report.json` writes JSON and suppresses stdout.
- `--language c --parse --no-color` is accepted.
- `--language c --parse --debug-traceback` is accepted.
- raw comment stripping, line-continuation folding, top-level splitting,
  include collection, simple macro collection, function-like macro diagnostics,
  conditional non-selection, simple declarations, variables, typedefs,
  parenthesized declarators, function pointer typedefs/parameters, recursive
  declarator combinations, concrete declaration objects, aggregate
  definitions/members/enumerators, incomplete struct/union tags, and function
  signatures with definition start/end locations are covered by focused C tests.
- valid reordered primitive specifiers and fatal invalid primitive-specifier
  combinations are covered by focused C tests.
- flexible array member classification/validation, per-member source
  locations, and named/unnamed/zero-width bit-field source facts are covered
  by focused C tests.
- `--show-vars` and `--print-limit` are rejected in C mode until C-specific
  display controls exist.
- `--semantics` with `--language c` is rejected until C semantic conversion is
  implemented.
- `--pyi` with `--language c` is rejected until C `.pyi` emission is
  implemented.

## Integration Order

Completed order:

1. Added CLI language selection behind explicit flags.
2. Kept Fortran as default behavior.
3. Added a C parser package and initial report provider.
4. Added C-specific docs for command shape and staged output.
5. Added CLI/API tests around discovery, stable command behavior, JSON, output
   files, public entrypoints, and diagnostic formatting.
6. Added raw lexer/directive metadata collection for comments,
   continuations, includes, simple macros, and unsupported function-like
   macros.
7. Added top-level splitting and a first partial grammar subset for simple
   variables, typedefs, function prototypes, and function-definition headers.
8. Added function-definition start/end locations while continuing to skip
   executable bodies.
9. Added forward `struct name;` extraction as incomplete `CStruct` source facts.
10. Replaced ad hoc declarator splitting with a recursive grammar-style
    declarator parser for pointer prefixes, parenthesized direct declarators,
    and array/function suffixes.
11. Classified each declarator from its recursive type and added basic
    struct/union/enum declarations, members, tag typedefs, and trailing tag
    variables as concrete parser models.
12. Replaced generic type references and declaration-kind tags with concrete
    `CType` subclasses, `CComposedType` components, and concrete declaration
    objects.
13. Added order-insensitive primitive specifier validation and `CPARSE003`
    errors for invalid primitive combinations while retaining unresolved
    typedef-name references for later resolution.
14. Added field-level source locations, flexible array member classification
    and invalid-use diagnostics, plus explicit bit-field regression coverage.

Next implementation work should continue with tag/typedef resolution,
preprocessed-input line mapping, compiler extension policy, and project
resolution while keeping the explicit `--language c` gate in place.
