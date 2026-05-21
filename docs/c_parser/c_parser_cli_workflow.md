# C Parser CLI Workflow Plan

Status: planning only. No C parser CLI implementation exists in this branch
yet.

The C parser CLI workflow should be designed before parser implementation so
future parser work lands behind a stable command shape, output schema, and
diagnostic contract.

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

Optional short alias:

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
  Macros: 0
  Includes: 0
  Parser status: skeleton
```

JSON output:

```json
{
  "include/example.h": {
    "language": "c",
    "parser_status": "skeleton",
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
parser_status
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
- a C-specific env var such as `C_PARSER_DEBUG=1` may be added
- `FORTRAN_PARSER_DEBUG` should not control C behavior
- a generic `X2PY_DEBUG=1` may be considered later

Color behavior:

- `--no-color` disables ANSI diagnostics
- `NO_COLOR=1` disables ANSI diagnostics
- Windows color behavior can follow the existing `colorama` pattern

## CLI Test Expectations

Phase 1 should add CLI tests before real parsing:

- Existing Fortran CLI tests still pass unchanged.
- `python -m x2py --help` lists `--language`.
- `python -m x2py <file.c> --language c --parse` is accepted.
- `python -m x2py <file.c> --parse-c` is accepted only if the alias is added.
- `--language c --parse --json` emits stable skeleton JSON.
- `--language c --parse --out report.json` writes JSON and suppresses stdout.
- `--language c --parse --no-color` affects C diagnostics.
- `--language c --parse --debug-traceback` re-raises `CParseError` once the
  error class exists.
- `--show-vars` remains Fortran-specific or is rejected for C until a C
  equivalent exists.
- `--semantics` with `--language c` is rejected until C semantic conversion is
  implemented.
- `--pyi` with `--language c` is rejected until C `.pyi` emission is
  implemented.

## Integration Order

1. Add CLI language selection behind explicit flags.
2. Keep Fortran as default behavior.
3. Add a skeleton C report provider with no parser logic.
4. Add C-specific docs for command shape and placeholder output.
5. Add CLI tests around discovery, stable command behavior, JSON, output
   files, and diagnostics.
6. Only then begin parser package/model work.
