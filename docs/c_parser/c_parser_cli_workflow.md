# C Parser CLI Workflow Plan

Status: C parser partial subset plus raw directive metadata implemented. The
CLI command shape exists and parse reports can include raw includes, simple
macros, `#undef` provenance, metadata diagnostics, simple globals, typedefs,
function prototypes, prototype-style metadata, and function-definition
signatures with start/end locations.

The C parser CLI workflow should be designed before parser implementation so
future parser work lands behind a stable command shape, output schema, and
diagnostic contract.

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
`globals`, `macros`, `includes`, and `diagnostics`. The current partial parser
can populate `functions`, `typedefs`, and `globals` for the supported subset,
while composite type sections remain empty. Raw `includes`, `macros`, and
metadata `diagnostics` can also be populated. The parser reports
`parser_status: "partial"`. C parse diagnostics, currently including
unsupported K&R-style function definitions, honor `--no-color` and `NO_COLOR=1`.
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

## Planned Flags

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
variable. The current grammar subset is tolerant for unsupported declaration
forms; targeted syntax diagnostics should be added alongside focused tests.

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
  Globals: 0
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
        "return_type": {
          "base": "int"
        },
        "parameters": [],
        "storage": [],
        "specifiers": [],
        "variadic": false,
        "is_definition": false,
        "prototype_style": "prototype",
        "start": {"filename": "include/example.h", "line": 1, "...": "..."},
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

The C parse JSON should be per-file and should not reuse Fortran key names when
the concepts differ. Proposed top-level per-file keys:

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
globals
macros
includes
diagnostics
```

Every model should include source-location metadata once implementation begins:

```text
source_location: {
  filename: str | null,
  line: int | null,
  column: int | null,
  source_line: str | null
}
```

## Human Tree Output

The tree should mirror the Fortran parser style: compact by default, expanded
with explicit flags.

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
    - struct vector (fields=2)
  Typedefs: 1
    - vector_t -> struct vector
  Macros: 1
    - MAX_DIM = 16
```

Future semantic readiness output should be described in the semantic-layer
documentation, not in the parser CLI workflow.

## Diagnostics Behavior

C parser errors should use a `CParseError` model with the same user experience
as `FortranParseError`:

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
  conditional non-selection, simple declarations, globals, typedefs, and
  function signatures with definition start/end locations are covered by focused C
  tests.
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
   globals, typedefs, function prototypes, and function-definition headers.
8. Added function-definition start/end locations while continuing to skip
   executable bodies.

Next implementation work should continue with richer declarator support,
preprocessed-input line mapping, composite types, and project resolution while
keeping the explicit `--language c` gate in place.
