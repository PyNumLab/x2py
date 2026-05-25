# C Parser CLI Workflow Plan

Status: C parser partial subset plus raw directive metadata implemented. The
CLI command shape exists and parse reports can include raw includes, simple
macros, `#undef` and conditional directive provenance, raw conditional
function variants, top-level redeclaration diagnostics, project include/index
metadata, diagnostics,
variables, typedefs,
aggregate declarations, function prototypes, prototype-style metadata, and
function-definition signatures with start/end locations. Declarator output can
represent parenthesized pointer/array precedence through concrete
`CComposedType` components and nameless `CFunctionType` signatures; function
parameters expose both declared and C-adjusted effective type facts. The CLI
also exposes shared C/Fortran preprocessing flags and can run exact
compiler/preprocessor executables for compiler mode. Target-specific standard
header type facts for C semantics are available through the separate
`python -m x2py.c_type_probe` command. C semantic IR, readiness, and starter
exact-contract `.pyi` output are available through the shared `x2py` CLI.

This document records the implemented C parse command shape, output schema,
and diagnostic contract, plus deferred CLI behavior.

## Current Status

Implemented commands:

```bash
python -m x2py path/to/api.h --language c --parse
python -m x2py path/to/api.h --language c --parse --json
python -m x2py path/to/api.h --language c --parse --out report.json
python -m x2py path/to/api.h --language c --parse --preprocess compiler --compiler clang-18 -I include -D API_EXPORT= --std c11
python -m x2py path/to/api.h --language c --semantics
python -m x2py path/to/api.h --language c --wrap-readiness
python -m x2py path/to/api.h --language c --pyi
```

The C parser accepts explicit `.c`, `.h`, and direct `.i` files, plus
directories in explicit C mode. Directory scanning in C mode collects those
three source forms. It does not recursively parse headers mentioned by
includes; as on the Fortran path, an imported/included source is parsed only
when the user supplied it or supplied a directory containing it.
Auto-detection is deferred, so omitting `--language` keeps the current Fortran
behavior.

The C parser output differs from Fortran parser output by using C-specific
top-level sections: `functions`, `structs`, `unions`, `enums`, `typedefs`,
`variables`, `macros`, `includes`, and `diagnostics`. The current partial parser
can populate `functions`, `typedefs`, `variables`, `structs`, `unions`, and
`enums` in the supported subset. Typedefs, variables, parameters, and aggregate
members can include concrete composed types for pointer/array/function forms,
including function pointers, functions returning function pointers, and
legal final flexible struct members marked with `is_flexible=True`. Array and
function parameters preserve written `declared_type` forms while effective
`type` values use pointer adjustment. Raw
`includes`, `macros`, `raw_directives`, `macro_dependencies`, and metadata
`diagnostics` can also be populated. `--preprocess compiler` runs an exact
user-supplied compiler/preprocessor executable or uses a C
`compile_commands.json` entry, then feeds the preprocessed stdout through the
same parser with `preprocessing: "compiler"`. `#line` and GCC/Clang
linemarkers remap parsed declarations and diagnostics back to the original
source. `parse_c_project(...)` additionally
populates project-level include/index fields such as `include_graph`,
`system_includes`, `unresolved_includes`, `functions_by_file`,
`enum_constants`, and `header_source_pairs`. Those fields require project
context; a single-file parse only records the local file facts. If raw
conditional branches expose incompatible alternatives of one function,
`CFunction.condition_set` records the alternatives and
`CProject.conditional_function_variants` retains them outside the unique
function index.
The object class distinguishes declarations (`CFunction`,
`CVariable`, `CTypedef`, `CStruct`, `CUnion`, or `CEnum`), and incomplete tag
declarations set `is_incomplete=True`.
Known unsupported declaration forms such as declaration attributes, alignment
specifiers, and static assertions are
reported in diagnostics with explicit `unit_kind` values; unconsumed declarator
suffixes are diagnosed instead of silently omitted. Invalid flexible array
member placement and flexible union members produce
`C_INVALID_FLEXIBLE_ARRAY_MEMBER` error diagnostics at the field location. The parser reports
`parser_status: "partial"`. C parse diagnostics, currently including
unsupported K&R-style function definitions and invalid primitive-specifier
combinations such as `unsigned float`, honor `--no-color` and `NO_COLOR=1`.
Active CLI regression tests also verify that `--debug-traceback` and
`C_PARSER_DEBUG=1` re-raise fatal C parse errors for debugging.
Function definitions do not store executable body text; they preserve a
direct `start` location and `end` location from the signature start through the
closing brace. Compatible repeated top-level declarations are merged;
prototype-plus-definition records prefer the definition and preserve prototype
locations in `declaration_locations`. File-scope tentative declarations such
as `int i; int i;` are also merged. Duplicate definitions and incompatible
top-level redeclarations are reported as diagnostics. Local declarations inside
function bodies are not parsed.

Unsupported C display controls:

```bash
python -m x2py path/to/api.h --language c --parse --show-vars
python -m x2py path/to/api.h --language c --parse --print-limit 20
```

Fortran-only parse display flags such as `--show-vars` and `--print-limit`
return clear argparse errors in C mode until C-specific display controls exist.

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

No separate `--parse-c` alias is provided. `--language c --parse` is the
single shared language-selection form.

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

Implemented shared preprocessing flags:

```text
--preprocess {internal,compiler}
--compiler EXACT_EXECUTABLE
--compile-commands PATH
-I DIR / --include-dir DIR
-D NAME[=VALUE] / --define NAME[=VALUE]
-U NAME / --undef NAME
--std STANDARD
--compiler-arg ARG
```

`--preprocess internal` is the default. For C it means the current raw
directive metadata mode: x2py reads `.h`/`.c` input directly, records includes
and macros from the file, parses ordinary visible declarations, and does not
expand macros or select `#if` branches. For Fortran it means the existing
internal preprocessing path, including simple macro branch selection through
`-D` and `-U`.

`--preprocess compiler` means x2py runs an external compiler/preprocessor and
parses stdout. The user must pass an exact compiler executable with
`--compiler`, unless a C `--compile-commands` entry supplies it. Do not rely on
generic defaults when multiple compiler versions are installed.

Before this mechanism is treated as portable across supported toolchains, it
needs substantial integration testing with multiple C and Fortran compiler
families and versions, including GCC/GFortran, Clang/LLVM-family tools, and
vendor compilers where available. That validation should cover command-line
flag compatibility, include and macro behavior, preprocessed stdout parsing,
and C `#line`/linemarker source-location remapping.

Standard-header typedefs and opaque handles require target ABI facts rather
than raw parser guesses. The standalone probe emits JSON intended for later C
semantic conversion:

```bash
python -m x2py.c_type_probe --compiler /usr/bin/gcc-13 --std c11

# Cross target: run the generated target executable under an emulator.
python -m x2py.c_type_probe --compiler aarch64-linux-gnu-gcc \
  --compiler-arg=--sysroot=/opt/aarch64-sysroot \
  --runner=qemu-aarch64 --runner=-L --runner=/opt/aarch64-sysroot
```

It reports `size_t`, available `uint32_t`, and `time_t` width/signedness
classification, plus opaque `FILE` pointer width/alignment, together with the
generated source and exact compile/run commands. The probe carries
target-relevant user flags: `-I`, `-D`, `-U`, and every `--compiler-arg`.
The requested `--std` is recorded in the report, but the generated C probe is
compiled as C11 because it uses `_Generic` and `_Alignof`. If a standard flag is
part of the target profile and is C11-compatible, pass it through
`--compiler-arg` so it appears in the actual compile command. The probe does
not read `compile_commands.json` directly; when parser preprocessing uses a
compile database, pass the selected compiler and target-relevant flags from the
matching entry to the probe explicitly. This is separate from parser JSON
because it describes a target ABI rather than a source declaration.

Fortran has the same target-profile issue for kind values. The Fortran semantic
path collects unresolved expressions such as `selected_real_kind(12)` and can
evaluate them through `x2py.fortran_type_probe` using the configured compiler,
`-I`, `-D`, `-U`, `--std`, and `--compiler-arg` flags. When the x2py CLI runs
Fortran `--semantics`, `--pyi`, or `--wrap-readiness` with `--preprocess
compiler --compiler ...`, those collected values are evaluated automatically
and passed into semantic conversion.

Examples:

```bash
# C, versioned executable from PATH.
python -m x2py include/api.h --language c --parse \
  --preprocess compiler \
  --compiler clang-18 \
  -I include \
  -D API_EXPORT= \
  -D FEATURE_X=1 \
  -U DEBUG \
  --std c11

# C, absolute compiler path.
python -m x2py src/api.c --language c --parse --json \
  --preprocess compiler \
  --compiler /usr/bin/gcc-13 \
  -I /opt/vendor/include \
  --compiler-arg=--sysroot=/opt/sdk

# C, Intel or vendor compiler path.
python -m x2py include/vendor_api.h --language c --parse \
  --preprocess compiler \
  --compiler /opt/intel/oneapi/compiler/latest/bin/icx \
  -D VENDOR_PUBLIC=

# C, project build database. The compiler and most flags come from the matching
# compile_commands.json entry for the input file.
python -m x2py src/api.c --language c --parse \
  --preprocess compiler \
  --compile-commands build/compile_commands.json

# Fortran, current internal branch selection.
python -m x2py src/solver.F90 --parse \
  -D USE_MPI \
  -U DEBUG

# Fortran, compiler-assisted preprocessing with an exact versioned executable.
python -m x2py src/solver.F90 --parse \
  --preprocess compiler \
  --compiler /usr/bin/gfortran-12 \
  -I include \
  -D USE_MPI \
  --std f2018

# Fortran, Intel compiler.
python -m x2py src/solver.F90 --parse \
  --preprocess compiler \
  --compiler /opt/intel/oneapi/compiler/latest/bin/ifx \
  -I include \
  -D USE_MPI
```

Flag meanings:

- `--compiler`: exact executable to run. Use `gcc-13`, `clang-18`,
  `/usr/bin/gfortran-12`, `/opt/.../ifx`, etc. x2py treats this as one argv
  item, not a shell command string.
- `--compile-commands`: C project database. x2py finds the entry for the input
  file, strips compile-only flags such as `-c` and `-o`, adds `-E`, and uses
  that entry's compiler unless `--compiler` overrides it.
- `-I` / `--include-dir`: include path passed as `-IDIR` in compiler mode. In
  C internal mode it is also used for quoted include resolution.
- `-D` / `--define`: macro definition. `-D NAME` means `NAME=1`; `-D NAME=VALUE`
  preserves `VALUE`.
- `-U` / `--undef`: macro undefinition. In Fortran internal mode this selects
  inactive branches for that macro.
- `--std`: language standard passed as `-std=STANDARD`, for example `c11`,
  `c23`, `f2008`, or `f2018`.
- `--compiler-arg`: one raw compiler argument. For values beginning with `-`,
  use the equals form, for example `--compiler-arg=-target`.

`--define` and `--undef` belong to compiler-assisted preprocessing for C, not
to raw parser-side macro evaluation. Raw C mode records directives and parses
ordinary visible declarations only; it does not select `#if` branches or expand
macros. A declaration prefixed by an unexpanded object-like macro is deferred
as macro-dependent rather than treated as an invalid type sequence.

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
        "end": null,
        "declaration_locations": []
      }
    ],
    "structs": [],
    "unions": [],
    "enums": [],
    "typedefs": [],
    "variables": [],
    "macros": [],
    "includes": [],
    "raw_directives": [],
    "macro_dependencies": [],
    "diagnostics": []
  }
}
```

The parser should not claim C files are wrappable. C readiness follows the
semantics-owned readiness boundary used elsewhere in x2py and does not become
parser JSON.

For raw directives, the same JSON shape is used, but `includes`, `macros`,
`raw_directives`, `macro_dependencies`, and `diagnostics` may contain populated
model dictionaries. Function-like macros are recorded as macro metadata and
also produce a non-fatal `C_UNSUPPORTED_FUNCTION_LIKE_MACRO` diagnostic.
Function-like declaration wrappers and object-like declaration prefixes are
marked through `macro_dependencies` without being parsed as expanded
declarations. Local quoted includes are resolved
relative to the current file or configured include dirs when possible;
unresolved local includes produce `C_UNRESOLVED_INCLUDE` diagnostics instead
of hard failures. Resolution records an edge; it does not make the included
file a parser input. System includes are recorded but neither searched nor
parsed recursively. Generated headers follow the same explicit-input rule.
Raw same-name functions in mutually exclusive conditional branches carry
`condition_set` branch tokens and are retained as alternatives rather than
misdiagnosed as incompatible redeclarations.

Raw mode must not claim support for macro-generated declarations. If macros
affect function names, types, parameters, attributes, storage classes, calling
conventions, visibility annotations, or active conditional branches, the user
should use `--preprocess compiler` with an exact compiler executable and the
same `-I`, `-D`, `-U`, standard, target, and sysroot flags required by their
build. The user should not normally pass a `.i` file directly; x2py generates
the preprocessed stream internally. Compiler/preprocessed mode preserves
`#line`/linemarker mappings so parser diagnostics and JSON `source_location`
fields point back to the original `.h` or `.c` file rather than the compiler
stdout stream. For streams generated by `x2py --preprocess compiler`, per-file
JSON also contains `preprocessing_recipe` with the exact compiler argv,
configuration flags, working directory, and selected `compile_commands.json`
entry when used. Parsed declarations from compiler mode carry
`origin: "preprocessed"`. Explicit or directory-discovered `.i` inputs are
also parsed as preprocessed source and record `preprocessed_source_path` plus
mapped `original_source_paths` when linemarkers supply original filenames.

## JSON Parse Schema

The C parse JSON is per-file and does not reuse Fortran key names when the
concepts differ. Current top-level per-file keys:

```text
language
filename
parser_status
preprocessing
preprocessing_recipe  # present for x2py-generated compiler input
preprocessed_source_path  # present for direct .i input
original_source_paths  # present when linemarkers identify original files
functions
structs
unions
enums
typedefs
variables
macros
includes
raw_directives
macro_dependencies
diagnostics
```

Declaration/directive records include `source_location`; diagnostics use
`location`. Concrete type components preserve `source_text` rather than their
own source-location object:

`condition_set` is emitted only for raw same-name `CFunction` alternatives
that survive normalization. For project-model JSON,
`conditional_function_variants` is emitted only when those alternatives
cannot be represented by one unique `functions` entry.

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
- No `--parse-c` alias is provided; C uses `--language c --parse`.
- `--language c --parse --json` emits stable partial-parser JSON with raw
  include/macro metadata and supported declarations when present.
- `--language c --parse --out report.json` writes JSON and suppresses stdout.
- `--language c --parse --no-color` is accepted.
- `--language c --parse --debug-traceback` is accepted.
- raw comment stripping, line-continuation folding, top-level splitting,
  include collection, simple macro collection, function-like macro diagnostics,
  object-like macro declaration-prefix deferral,
  conditional non-selection and mutually exclusive function variants, simple
  declarations, variables, typedefs,
  parenthesized declarators, function pointer typedefs/parameters, recursive
  declarator combinations, concrete declaration objects, aggregate
  definitions/members/enumerators, incomplete struct/union tags, and function
  signatures with definition start/end locations are covered by focused C tests.
- valid reordered primitive specifiers and fatal invalid primitive-specifier
  combinations are covered by focused C tests.
- flexible array member classification/validation, per-member source
  locations, and named/unnamed/zero-width bit-field source facts are covered
  by focused C tests.
- array and function parameter declared/effective type adjustment is covered
  by focused C tests.
- `--show-vars` and `--print-limit` are rejected in C mode until C-specific
  display controls exist.
- `--semantics`, `--wrap-readiness`, and `--pyi` with `--language c` use
  `semantics.c2ir`, the semantic readiness checker, and the shared `.pyi`
  emitter for the supported exact-contract subset.

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
15. Added C array/function parameter adjustment while preserving written
    parameter type facts in `declared_type`.
16. Added compiler/preprocessed `#line` and GCC/Clang linemarker remapping for
    parsed source locations, parser diagnostics, and fatal parse errors.
17. Added optional JSON preprocessing recipes for x2py-generated compiler
    streams in C and Fortran, plus internal Fortran `-D`/`-U` selection.
18. Added C declaration-level preprocessed origin metadata and direct `.i`
    discovery/source-identity handling.
19. Preserved braced and designated initializer source text as `CInitializer`
    facts on parsed file-scope variables.
20. Parsed nested anonymous struct/union members as concrete member types,
    including recursively mapped preprocessed provenance.
21. Added `_Atomic(type)` type-specifier parsing on the shared declarator path
    and executable parser-developer walkthrough tests.
22. Added compiler-derived standard-header ABI probing for C semantic mapping
    without hard-coded host type aliases.
23. Added C semantic IR, readiness, and starter exact-contract `.pyi` output
    through `x2py --language c`.

Next implementation work should continue with fixture-driven compiler
extension policy and broader project conflict policy
while keeping the explicit `--language c` gate in place.
