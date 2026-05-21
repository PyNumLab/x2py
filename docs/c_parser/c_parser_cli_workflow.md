# C Parser CLI Workflow Plan

Status: C parser skeleton implemented. The CLI command shape and stable empty
parse report exist, but no real C declarations are parsed yet.

The C parser CLI workflow should be designed before parser implementation so
future parser work lands behind a stable command shape, output schema, and
diagnostic contract.

## Current Status

Implemented skeleton commands:

```bash
python -m x2py path/to/api.h --language c --parse
python -m x2py path/to/api.h --language c --parse --json
python -m x2py path/to/api.h --language c --parse --out report.json
```

The skeleton accepts explicit `.c` and `.h` files, plus directories in
explicit C mode. Directory scanning in C mode only collects `.c` and `.h`
files. Auto-detection is deferred, so omitting `--language` keeps the current
Fortran behavior.

The C parser output differs from Fortran parser output by using C-specific
top-level sections: `functions`, `structs`, `unions`, `enums`, `typedefs`,
`globals`, `macros`, `includes`, and `diagnostics`. During the skeleton phase
all of those lists are empty and `parser_status` is `"skeleton"`.

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

Optional short alias, not implemented in the skeleton:

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

Skeleton behavior also accepts `--no-color`. `CParseError` already supports
compiler-style diagnostic formatting and the `C_PARSER_DEBUG` environment
variable, although the skeleton parser does not yet raise syntax diagnostics
for declaration-shaped input.

C-specific flags to add only when needed:

```text
--include-dir PATH
--define NAME[=VALUE]
--undef NAME
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
```

## Early Skeleton Behavior

Phase 1 may implement CLI structure before a real parser exists. Skeleton
behavior should be intentionally stable:

```bash
x2py include/example.h --language c --parse
```

Human output:

```text
File: include/example.h
  Language: c
  Functions: 0
  Structs: 0
  Unions: 0
  Enums: 0
  Typedefs: 0
  Globals: 0
  Macros: 0
  Includes: 0
  Diagnostics: 0
  Parser status: skeleton
```

JSON output:

```json
{
  "include/example.h": {
    "filename": "include/example.h",
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

The skeleton should not claim C files are wrappable. If C readiness is added
later, it should follow the semantics-owned readiness boundary used elsewhere
in x2py, not become parser JSON.

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

Phase 1 has CLI tests before real parsing:

- Existing Fortran CLI tests still pass unchanged.
- `python -m x2py --help` lists `--language`.
- `python -m x2py <file.c> --language c --parse` is accepted.
- `python -m x2py <file.c> --parse-c` is not implemented in the skeleton.
- `--language c --parse --json` emits stable skeleton JSON.
- `--language c --parse --out report.json` writes JSON and suppresses stdout.
- `--language c --parse --no-color` is accepted; real diagnostic color tests
  will matter once parser errors can be raised by C syntax.
- `--language c --parse --debug-traceback` is accepted.
- `--show-vars` and `--print-limit` are rejected in C mode until C-specific
  display controls exist.
- `--semantics` with `--language c` is rejected until C semantic conversion is
  implemented.
- `--pyi` with `--language c` is rejected until C `.pyi` emission is
  implemented.

## Integration Order

Completed skeleton order:

1. Added CLI language selection behind explicit flags.
2. Kept Fortran as default behavior.
3. Added a C parser package and skeleton C report provider with no grammar
   parsing.
4. Added C-specific docs for command shape and placeholder output.
5. Added CLI/API tests around discovery, stable command behavior, JSON, output
   files, public entrypoints, and diagnostic formatting.

Next implementation work should begin with lexer/preprocessor and declaration
model behavior while keeping the explicit `--language c` gate in place.
