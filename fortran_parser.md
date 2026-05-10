# Fortran parser reference (wrapper-focused subset)

This document defines the currently supported parser subset, expected behavior,
and practical usage from terminal and Python.

## 1) Supported features (comprehensive)

### 1.1 Source forms and preprocessing

- Free-form Fortran: `.f90`, `.f95`, `.f03`, `.f08`
- Fixed-form Fortran: `.f`, `.for`, `.ftn`
- Free/fixed comment stripping
- Continuation handling for both forms

### 1.2 Procedure parsing

- `subroutine` headers
- `function` headers
- Header modifiers: `pure`, `elemental`, `recursive`
- Function `result(...)` parsing (tolerant support for `results(...)`)

### 1.3 Declaration/argument parsing

- Intrinsic types: `integer`, `real`, `complex`, `logical`, `character`
- Kind extraction from declaration specs (`kind=...`)
- Attribute extraction:
  - `intent(in|out|inout)`
  - `optional`
  - `value`
  - `allocatable`
  - `pointer`
- Array extraction:
  - `dimension(...)`
  - variable-level shape syntax (`x(:)`, `x(n)`)

### 1.4 Modules, imports, and project context

- Module discovery
- Module variable extraction
- `use` extraction at module and procedure scope
- Propagation of module-level `use` imports into contained procedures
- Folder/project parsing with dependency-aware ordering
- Cross-file kind constant resolution (e.g., kinds modules)

### 1.5 Derived type parsing

- `type :: ... end type` discovery
- Type attributes (e.g., `abstract`)
- Inheritance (`extends(parent)`)
- Field extraction including shape/pointer/allocatable
- Type-bound procedures:
  - `procedure ... :: ...` bindings with attributes (e.g. `pass(self)`, `nopass`)
  - `generic ... :: name => target1, target2`

### 1.6 Readiness diagnostics

- Unsupported-pattern checks
- Unknown argument declaration reporting
- Final boolean readiness (`wrappable`)

## 2) Public API surface

- `parse_fortran_signatures`
- `parse_fortran_types`
- `parse_fortran_modules`
- `parse_fortran_project_signatures`
- `parse_fortran_namespace`
- `assess_wrap_readiness`

## 3) Terminal usage and expected outputs

### 3.1 Basic CLI invocation

```bash
python -m fortran_parser <path ...>
```

or (if installed as a console script):

```bash
fortran-parser <path ...>
```

`<path ...>` supports files and directories. Directories are recursively scanned
for `.f`, `.for`, `.ftn`, `.f90`, `.f95`, `.f03`, `.f08`.

### 3.2 Human-readable output example

Input Fortran (`tests/fcode/basic_subroutine.f90`):

```fortran
module m1
  implicit none
  integer :: n
  real, dimension(10) :: x
contains
  subroutine add1(n, x)
    integer, intent(in) :: n
    real, dimension(n), intent(inout) :: x
  end subroutine add1
end module m1
```

Command:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90
```

Expected output shape:

```text
File: tests/fcode/basic_subroutine.f90
  Modules: 1
    - module m1 (vars=2, uses=0)
      Procedures: 1
        - subroutine add1(n:integer[0], x:real[1])
```

Interpretation:

- Parsed entities are counted per file.
- Free procedures (outside modules) are shown in top-level `Procedures`.
- Module-contained procedures are nested under each module.
- Empty sections are omitted from the human-readable report.

More complex example:

Input Fortran (`mixed_example.f90`):

```fortran
subroutine driver(n)
  integer, intent(in) :: n
end subroutine driver

module math_ops
  use iso_c_binding, only: c_double
  implicit none
  real(c_double) :: alpha
contains
  subroutine saxpy(n, a, x, y)
    integer, intent(in) :: n
    real(c_double), intent(in) :: a
    real(c_double), dimension(n), intent(in) :: x
    real(c_double), dimension(n), intent(inout) :: y
  end subroutine saxpy

  function dot(x, y) result(r)
    real(c_double), dimension(:), intent(in) :: x, y
    real(c_double) :: r
  end function dot
end module math_ops

module io_ops
  implicit none
contains
  subroutine dump(v)
    real, dimension(:), intent(in) :: v
  end subroutine dump
end module io_ops
```

Command:

```bash
python -m fortran_parser mixed_example.f90
```

```text
File: mixed_example.f90
  Procedures: 1
    - subroutine driver(n:integer[0])
  Modules: 2
    - module math_ops (vars=1, uses=1)
      Procedures: 2
        - subroutine saxpy(n:integer[0], a:real[0], x:real[1], y:real[1])
        - function dot(x:real[1], y:real[1])
    - module io_ops (vars=0, uses=0)
      Procedures: 1
        - subroutine dump(v:real[1])
```

### 3.3 JSON output example

Print JSON:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json
```

Write JSON:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json-out report.json
```

Print + write:

```bash
python -m fortran_parser tests/fcode/basic_subroutine.f90 --json --json-out report.json
```

Expected JSON layout:

- Top-level object keyed by input path
- Per-file payload with keys:
  - `signatures`
  - `types`
  - `modules`
  - `wrap_readiness`

### 3.4 Parse-error diagnostics and debug mode

When parsing fails, the CLI prints a compiler-style diagnostic to `stderr` and
exits with status code `1`. By default this output is intended for end users: it
includes the source location, diagnostic code, message, source line, and caret
context, but it does **not** include a Python traceback.

Example command:

```bash
python -m fortran_parser tests/fcode/errors/err_duplicate_argument_name.f90
```

Example diagnostic shape:

```text
tests/fcode/errors/err_duplicate_argument_name.f90:1:1: error[PARSE001]: Duplicate argument name 'x' in procedure 'dup'.
  |
1 | subroutine dup(x, y, x)
  | ^
```

ANSI color is enabled by default when available; no color flag is needed for
normal use. To disable color explicitly, pass `--no-color` or set the standard
`NO_COLOR` environment variable:

```bash
python -m fortran_parser bad.f90 --no-color
NO_COLOR=1 python -m fortran_parser bad.f90
```

For parser development, use `--debug-traceback` to re-raise
`FortranParseError` and let Python print the full traceback showing where the
error was raised internally:

```bash
python -m fortran_parser bad.f90 --debug-traceback
```

The same developer mode can be enabled with the environment variable
`FORTRAN_PARSER_DEBUG=1`:

```bash
FORTRAN_PARSER_DEBUG=1 python -m fortran_parser bad.f90
```

In debug mode, the traceback's final exception message also includes a
`note: parser raised at ...` line with the internal parser file, line, and
function that created the diagnostic.

## 4) Python usage and expected outputs

### 4.1 Parse folder namespace

```python
from fortran_parser import parse_fortran_namespace

namespace = parse_fortran_namespace("tests/fcode")
print(namespace.keys())
print(len(namespace["signatures"]))
```

Expected behavior:

- Recursively scans Fortran files.
- Resolves dependencies and module imports across files.
- Returns aggregate namespace parse output.

### 4.2 Parse single file and run readiness check

```python
from pathlib import Path
from fortran_parser import parse_fortran_signatures, assess_wrap_readiness

p = Path("tests/fcode/basic_subroutine.f90")
code = p.read_text()

signatures = parse_fortran_signatures(code, filename=str(p))
readiness = assess_wrap_readiness(code, filename=str(p))

print("signatures", len(signatures))
print("wrappable", readiness["wrappable"])
print("unsupported", readiness["unsupported_hits"])
```

Expected behavior:

- `signatures` is a normalized list of callable records.
- `readiness` includes counts, unsupported hits, unknown args, and `wrappable`.

## 5) Running tests

Run all tests:

```bash
PYTHONPATH=. pytest -q
```

Run parser-focused tests:

```bash
PYTHONPATH=. pytest -q tests/test_fortran_signature_parser.py
PYTHONPATH=. pytest -q tests/test_fortran_fixture_suite.py
PYTHONPATH=. pytest -q tests/test_cli.py
```

Update golden JSON fixtures:

```bash
python tests/fcode/generate_fortran_parser_goldens.py
```

Update selected fixture(s):

```bash
python tests/fcode/generate_fortran_parser_goldens.py tests/fcode/basic_subroutine.f90
```

In-test auto-update mode:

```bash
FORTRAN_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/test_fortran_fixture_suite.py --confcutdir=tests/
```

## 6) Error handling

All parse failures raise `FortranParseError`, a subclass of `ValueError`. The
exception keeps structured metadata for consumers:

- `filename` — source path supplied to the parser, if any
- `line_number` — 1-based source line where the error was detected, if known
- `source_line` — original source text for context, if known
- `base_message` — stable error text without location/source context
- `code` — diagnostic code; the default parse diagnostic code is `PARSE001`

`str(error)` and `error.format_diagnostic(color=False)` render a
compiler-style diagnostic:

```text
<filename>:<line>:1: error[PARSE001]: <message>
  |
<N> | <source line>
  | ^
```

If no filename is available, the location is rendered as `<unknown>`. If a line
number or source line is unavailable, that part of the diagnostic is omitted or
shown with `?` as appropriate. Use `error.base_message` when tests or API
consumers need only the message text.

`format_diagnostic(color=True)` adds ANSI styling. The CLI requests colored
diagnostics by default when available; pass `--no-color` or set `NO_COLOR=1` to
disable ANSI output. On Windows, ANSI console compatibility is enabled through
`colorama` when it is installed.

For parser development, `format_diagnostic(debug=True)` appends a note with the
internal parser file, line, and function that raised the error. The CLI exposes
this through `--debug-traceback` or `FORTRAN_PARSER_DEBUG=1`; normal CLI parse
errors intentionally hide Python tracebacks.

The sections below list each error category, the triggering condition, and the
exact `base_message` format (with `<...>` placeholders for runtime values).

### 6.1 Unknown or unsupported type declaration

Triggered when a declaration line cannot be matched to any known intrinsic type,
`type(...)`, or `character` variant.

**In a procedure:**

```
Unknown or unsupported datatype declaration for procedure '<name>': <line>
```

Example Fortran that triggers this:

```fortran
subroutine bad(x)
  weirdtype :: x
end subroutine bad
```

Example error:

```
bad.f90:2:1: error[PARSE001]: Unknown or unsupported datatype declaration for procedure 'bad': weirdtype :: x
  |
2 |   weirdtype :: x
  | ^
```

**In a derived type:**

```
Unknown or unsupported datatype declaration in type '<name>': <line>
```

**In a module:**

```
Unknown or unsupported datatype declaration in module '<name>': <line>
```

### 6.2 Duplicate declaration

Triggered when the same symbol is declared more than once in the same scope.

**In a procedure (arguments and local declarations):**

```
Duplicate declaration of symbol '<name>' in procedure '<proc>'.
```

Example:

```fortran
subroutine dup(x)
  real :: x
  integer :: x
end subroutine dup
```

Example error:

```
dup.f90:3:1: error[PARSE001]: Duplicate declaration of symbol 'x' in procedure 'dup'.
  |
3 |   integer :: x
  | ^
```

**PARAMETER constants:**

```
Duplicate PARAMETER declaration of symbol '<name>' in procedure '<proc>'.
```

**In a derived type:**

```
Duplicate field '<name>' in derived type '<type>'.
```

**In a module:**

```
Duplicate variable '<name>' in module '<module>'.
```

### 6.3 Duplicate procedure name

Triggered when the same procedure name appears more than once within the same
module or global scope.

**Global scope:**

```
Duplicate procedure name '<name>' in global scope.
```

**Module scope:**

```
Duplicate procedure name '<name>' in module '<module>'.
```

Example:

```fortran
subroutine work(n)
  integer, intent(in) :: n
end subroutine work

subroutine work(n)
  integer, intent(in) :: n
end subroutine work
```

Example error:

```
dup.f90:5:1: error[PARSE001]: Duplicate procedure name 'work' in global scope.
  |
5 | subroutine work(n)
  | ^
```

### 6.4 Duplicate argument name

Triggered when a procedure's argument list contains the same name more than once.

```
Duplicate argument name '<name>' in procedure '<proc>'.
```

Example:

```fortran
subroutine dup(x, y, x)
  integer, intent(in) :: x
  real, intent(in) :: y
end subroutine dup
```

Example error:

```
dup_arg.f90:1:1: error[PARSE001]: Duplicate argument name 'x' in procedure 'dup'.
  |
1 | subroutine dup(x, y, x)
  | ^
```

### 6.5 Star-kind in modern source

Triggered when a legacy `type*N` (e.g. `real*8`) declaration appears in a file
with a modern Fortran extension (`.f90`, `.f95`, `.f03`, `.f08`).

```
Unsupported Fortran 77 star-kind declaration '<type>*<kind>' in modern source '<filename>'.
```

Example:

```fortran
subroutine bad(x)
  real*8 :: x
end subroutine bad
```

Example error (file `bad.f90`):

```
bad.f90:2:1: error[PARSE001]: Unsupported Fortran 77 star-kind declaration 'real*8' in modern source 'bad.f90'.
  |
2 |   real*8 :: x
  | ^
```

### 6.6 Fortran 77 syntax in a `.f77` source file

Triggered when modern constructs (`module`, `contains`, `interface`,
`class(...)`) appear in a file with extension `.f77`.

```
Unsupported syntax for Fortran 77 source '<filename>': <line>
```

Example:

```fortran
      module bad_module
      end module bad_module
```

Example error (file `legacy.f77`):

```
legacy.f77:1:1: error[PARSE001]: Unsupported syntax for Fortran 77 source 'legacy.f77': module bad_module
  |
1 |       module bad_module
  | ^
```

### 6.7 Implicit none — undeclared argument or result

Triggered when `implicit none` is active and an argument (or function result)
has no matching type declaration.

**Argument:**

```
Argument '<name>' in procedure '<proc>' has no type declaration (implicit none is active).
```

**Function result:**

```
Function result '<name>' in procedure '<proc>' has no type declaration (implicit none is active).
```

Example:

```fortran
subroutine foo(x, y)
  implicit none
  integer, intent(in) :: x
end subroutine foo
```

Example error:

```
implicit_none.f90:1:1: error[PARSE001]: Argument 'y' in procedure 'foo' has no type declaration (implicit none is active).
  |
1 | subroutine foo(x, y)
  | ^
```

### 6.8 Unknown datatype for function result

Triggered when a function result has no resolvable type after parsing (and
`implicit none` prevents implicit typing).

```
Unknown datatype for function result '<name>' in procedure '<proc>'.
```

Example:

```fortran
function f(x) result(res)
  implicit none
  real :: x
end function f
```

Example error:

```
bad.f90:1:1: error[PARSE001]: Unknown datatype for function result 'res' in procedure 'f'.
  |
1 | function f(x) result(res)
  | ^
```

### 6.9 Unknown datatype for a module variable

Triggered by `_validate_module_variables` when a parsed module variable still
has `base_type == "unknown"` after declaration parsing.

```
Unknown type for variable '<name>' in module '<module>'.
```

### 6.10 Unknown datatype for a derived type field

Triggered by `_validate_derived_type_fields` when a field still has
`base_type == "unknown"`.

```
Unknown type for field '<name>' in derived type '<type>'.
```

### 6.11 PARAMETER symbol without type in `implicit none` scope

Triggered when a legacy `PARAMETER (...)` statement names a symbol that has not
been typed and `implicit none` is in effect.

```
Unknown datatype for PARAMETER symbol '<name>' in procedure '<proc>'.
```

Example:

```fortran
      subroutine cst(a)
      implicit none
      real a
      parameter ( zero = 0.0e+0 )
      end
```

Example error:

```
legacy.f:4:1: error[PARSE001]: Unknown datatype for PARAMETER symbol 'zero' in procedure 'cst'.
  |
4 |       parameter ( zero = 0.0e+0 )
  | ^
```

### 6.12 Function result variable shadows an argument

Triggered when a `result(name)` clause reuses an argument name (and the two
names are different from each other — the special case `result(f)` on a
function named `f` is allowed).

```
Function result variable '<result>' in function '<func>' shadows an argument name.
```

Example:

```fortran
function f(res) result(res)
  integer, intent(in) :: res
end function f
```

Example error:

```
shadow.f90:1:1: error[PARSE001]: Function result variable 'res' in function 'f' shadows an argument name.
  |
1 | function f(res) result(res)
  | ^
```

### 6.13 Failed to resolve declared argument

An internal safety check: if a symbol was explicitly declared but its type
could not be applied (a parser regression guard), the following error is raised.

```
Failed to resolve declared argument '<name>' in procedure '<proc>'.
```

## 7) Scope note

This parser is intentionally wrapper-focused and not a complete Fortran front
end. Unsupported syntax should be surfaced through diagnostics/readiness output
for incremental parser extension.
