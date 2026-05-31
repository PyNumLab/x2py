# C Parser Reference

Status: current reference for the partial C frontend. The `c_parser`
package, typed parser models, explicit C CLI parse path, raw directive
metadata, compiler-assisted preprocessing, source-location remapping, project
indexes, parser goldens, C standard-type probe, first semantic IR conversion
subset, semantic readiness path, and starter exact-contract C `.pyi`
generation are implemented.

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

## Source Coverage

Supported source forms:

- `.c`
- `.h`
- `.i` preprocessed C input

Project input accepts explicit files and directories in explicit C mode.
Directory scanning in C mode discovers C source/header inputs without changing
Fortran's default directory behavior. Project parsing does not recursively
parse files named by C includes: as with Fortran recorded imports/includes,
only user-supplied files or files beneath a user-supplied directory are parsed.

## Current Status

Implemented:

- `c_parser` package
- typed C parser models for partial parse reports and raw metadata
- `CParser`, `parse_c_file`, and `parse_c_project`
- top-level `x2py.parse_c_file` and `x2py.parse_c_project` exports alongside
  the `c_parser` package entrypoints
- `CParseError` with compiler-style diagnostic formatting
- explicit `x2py --language c --parse` output
- explicit `x2py --language c --semantics` and
  `x2py --language c --wrap-readiness` output
- starter exact-contract `x2py --language c --pyi` output for the supported C
  semantic subset
- C JSON partial output and `--out` behavior
- raw lexer records with comment stripping, line-continuation folding, and
  lightweight token source locations
- top-level source splitting that tracks braces, parentheses, brackets, and
  string/character literals
- raw conditional same-name function alternatives retain Fortran-style
  `condition_set` branch identity rather than being diagnosed as conflicting
  redeclarations
- raw `#include` collection for quoted and system includes
- simple object-like `#define` macro collection
- function-like macro metadata with unsupported diagnostics
- object-like declaration-prefix macro dependencies deferred in raw mode
- raw `#undef` directive provenance in macro metadata
- concrete primitive `CType` objects, pointer/array composition, and concrete
  qualifier objects
- order-insensitive primitive specifier matching with
  `CPARSE_INVALID_SPECIFIER_SEQUENCE` errors for
  invalid combinations such as `unsigned float`
- recursive declarator extraction for parenthesized pointer/array precedence
- nameless `CFunctionType` signatures for function pointer typedefs and
  parameter source facts
- parameter array/function adjustment that keeps written `declared_type` facts
  and exposes effective pointer `type` facts
- simple file-scope variable and `typedef` extraction
- incomplete `struct name;` and `union name;` extraction as concrete tag types
  with `is_incomplete=True`
- named and anonymous struct/union/enum definitions
- aggregate member extraction as `CVariable` objects through the declarator
  backend, including pointer, array, callback-pointer, flexible-array, and
  bit-field source facts with per-member locations
- conservative parser diagnostics for function signatures that use unions by
  value, while pointer-to-union signatures remain ordinary parser facts
- inline tag typedef aliases and trailing tag object declarators as separate
  concrete models
- simple function prototype extraction
- prototype-style metadata distinguishing `int f(void)` from `int f()`
- simple function-definition signature extraction with body skipping
- start/end locations for function definitions, from the signature start
  through the closing brace
- braced and designated initializer source preservation on `CVariable`
- nested anonymous struct/union member definitions as concrete member types
- `_Atomic(type)` type specifiers, preserving the qualified outermost type
  component
- compiler/preprocessed input parsing through the same grammar path with
  `#line`/GCC linemarker remapping for parsed declarations and diagnostics
- declaration-level `origin="preprocessed"` metadata plus generated/original
  source identity for direct `.i` input where linemarkers provide it
- optional `preprocessing_recipe` JSON on `CFile` output for compiler streams
  generated by the shared x2py CLI
- compiler-derived standard-library ABI probing for `size_t`, `uint32_t`,
  `time_t`, and opaque `FILE` handles through `x2py.c_type_probe`
- C directory/file-list discovery for `.c`, `.h`, and direct `.i` inputs in
  explicit C mode, while leaving Fortran directory scanning unchanged
- include resolution for quoted includes relative to the current file and
  configured include directories, unresolved include tracking, system include
  tracking, cycle-safe include graph construction, and header/source pairing,
  without recursive include parsing
- project indexes for functions, file-scope variables, typedefs, struct tags,
  union tags, enum tags, enum constants, macros/constants, and functions by
  file; raw conditional alternatives that cannot occupy one unique function
  index entry are retained in `conditional_function_variants`
- basic cross-file typedef chain and struct/union/enum tag resolution, with
  typedef-cycle diagnostics and unresolved references preserved for later
  diagnostics
- unsupported K&R function-definition diagnostics
- C parser project JSON goldens and fatal diagnostic goldens generated from
  stable `CProject.to_dict()` and `CParseError` output
- C fixture inputs under `tests/data/c/general/`, diagnostic inputs under
  `tests/data/c/errors/parser/`, and partial-parser regression inputs under
  `tests/data/c/json/`, `tests/data/c/tinyexpr/`, `tests/data/c/linmath/`,
  `tests/data/c/nanosvg/`, and top-level C inputs from `tests/data/c/stb/`
- `semantics.c2ir` conversion for the first identity subset: scalar
  functions, const/mutable pointer storage contracts, declared arrays,
  structs/opaque structs, enums, numeric macro constants, local typedef
  chains, standard-type probe facts, and explicit semantic readiness blockers

Still deferred:

- callback policy metadata beyond parser-side callback candidates
- broad compiler-extension declarators
- broader typedef/tag conflict policy beyond the implemented basic project
  resolution
- richer C ownership/callback projection policy beyond exact starter `.pyi`
  stubs

## Supported C Subset

The supported subset focuses on stable wrapper-relevant APIs:

- function prototypes
- function definitions with extractable signatures
- primitive C scalar types
- pointers
- arrays in parameters and aggregate members
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
- compiler/preprocessed-mode tolerance for common GCC/Clang and MS declaration syntax:
  GNU attributes, `__declspec(...)`, `[[...]]`, `__extension__`, alternate
  qualifier/inline spellings, declaration-level `asm(...)`, calling-convention
  keywords, `typeof(...)`, `_BitInt(...)`, and selected extended scalar names

## Unsupported And Deferred Subset

The C parser explicitly reports or defers:

- full compiler-grade C parsing
- full preprocessor compatibility
- arbitrary macro expansion
- token pasting and stringification
- macro-generated declarations
- complex conditional compilation evaluation
- arbitrary GCC extensions
- arbitrary MSVC extensions
- C++ parsing
- K&R style function definitions
- full ABI generation
- guaranteed struct layout computation
- full bitfield ABI interpretation
- inline assembly
- `_Generic` semantic evaluation
- atomic operation semantics and validation beyond parsed type facts
- full semantic modeling of compiler attributes, calling conventions, assembler
  aliases, `typeof(...)`, `_BitInt(...)`, and extended scalar ABI facts

## Preprocessing Policy

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
- record conditional and pragma directives as raw provenance metadata,
  including OpenMP declaration pragmas such as `#pragma omp declare simd` and
  `#pragma omp declare target`
- retain mutually exclusive same-name function declarations as alternatives
  with `CFunction.condition_set` branch identity, matching the Fortran
  parser's unselected-branch convention
- record function-like macros as metadata with unsupported/deferred diagnostics
- record function-like wrappers and object-like declaration prefixes as
  macro-dependency metadata without claiming they were parsed
- parse only declarations that are already visible as ordinary C without macro
  expansion
- do not select active conditional branches from `#if`/`#ifdef` in raw mode
- do not expand macros, token pasting, stringification, or macro-generated
  declarations

Compiler-assisted preprocessing is the required path when macros affect the
declaration text that the C parser needs to understand. Use compiler mode when
macros define or alter function names, return types, parameter types,
declarators, attributes, storage classes, calling conventions, visibility
annotations, or conditional API selection. The user normally gives x2py `.h`
or `.c` files and has it run the configured compiler/preprocessor; direct
`.i` preprocessed inputs are also accepted and use their linemarkers for
locations and source identity.

Examples:

```bash
python -m x2py include/api.h --language c --parse \
  --preprocess compiler \
  --compiler clang-18 \
  -I include \
  -D API_EXPORT= \
  --std c11

python -m x2py src/api.c --language c --parse \
  --preprocess compiler \
  --compiler /usr/bin/gcc-13 \
  --compiler-arg=--sysroot=/opt/sdk

python -m x2py src/api.c --language c --parse \
  --preprocess compiler \
  --compile-commands build/compile_commands.json
```

`--compiler` must be the exact executable x2py should run. Versioned names
such as `gcc-13`, `clang-18`, and `/usr/bin/gfortran-12` are preferred over a
generic `gcc`, `clang`, or `gfortran` when several compiler versions are
installed.

Preprocessed mode preserves line mapping. The parser reads
compiler-preprocessed text, including `#line`/linemarker directives, and maps
every parsed declaration, source location, and diagnostic back to the original
`.h` or `.c` file and line number where possible. Without this mapping, errors
and JSON source locations would point at a generated `.i` file or temporary
preprocessor stream instead of the user's source.

This means macro-heavy APIs are still in scope. The boundary is that x2py v1
should not implement recursive, compiler-compatible macro expansion
internally; it should consume compiler-preprocessed output with preserved line
mapping. When the shared x2py CLI generates a compiler-preprocessed stream, it
stores `preprocessing_recipe` in the per-file `CFile` JSON: compiler
executable, final argv, include dirs, defines, undefines, standard, extra
arguments, working directory, and optional selected `compile_commands.json`
entry. Parsed declarations from compiler or direct `.i` input carry
`origin="preprocessed"`; direct `.i` files also expose
`preprocessed_source_path` and mapped `original_source_paths` where available.

## Standard Type ABI Probe

Types introduced by standard headers are not portable primitive aliases.
`size_t`, `uint32_t`, and `time_t` may depend on the compiler target, and
`FILE` should remain an opaque library handle rather than exposing private
library layout. Raw parsing therefore preserves unresolved typedef-name uses
instead of hard-coding an ABI.

For C semantic conversion, `x2py.c_type_probe` compiles and runs a small
C11 query program under an exact compiler and emits target-specific JSON:

```bash
python -m x2py.c_type_probe --compiler /usr/bin/gcc-13 --std c11
```

The report records arithmetic category, underlying C spelling, bit width, and
alignment for `size_t`, available `uint32_t`, and `time_t`; it records opaque
handle and pointer ABI facts for `FILE`. It also retains the generated C source
and exact compile/run commands.

The probe must be run with the same target profile as the source being parsed.
It carries `-I`, `-D`, `-U`, and `--compiler-arg` options into the compile
command because ABI and standard-header typedef facts can change with target
flags, sysroots, library headers, and compiler options. The requested `--std`
is retained as provenance; the generated query is compiled as C11 because it
uses C11 `_Generic` and `_Alignof`. If a standard-selection flag affects the
target profile and is compatible with the probe source, pass it through
`--compiler-arg` so it is part of the actual compile command.
The probe does not consume `compile_commands.json` directly; if parser
preprocessing uses a compile database, pass the selected compiler and
target-relevant flags from the matching entry to the probe explicitly.

For cross targets, provide a runner, for example `--runner=qemu-aarch64
--runner=-L --runner=/opt/aarch64-sysroot`.

The C semantic converter accepts this report as target context. The parser
model remains source-faithful and does not embed host ABI assumptions.

## Parser Organization Notes

`c_parser/parser.py` is intentionally ordered for maintainers. Read it from
top to bottom in these sections:

1. Parser constants, private grammar dataclasses, and small path helpers.
2. `CParser` public visitors: `visit_file`, `visit_project`, and
   `visit_parsed_project`.
3. Source-location, diagnostic, macro-provenance, and redeclaration helpers.
4. Declaration-specifier and compiler-extension lexical helpers.
5. Recursive declarator grammar and parameter helpers.
6. Function and aggregate visitors.
7. Translation-unit dispatch and project assembly.
8. Thin module-level wrappers: `parse_c_file` and `parse_c_project`.

Helper methods remain on `CParser` when they depend on parser state. Their
docstrings describe the narrow parsing responsibility and include examples
where call shape or grammar behavior is not obvious.

`visit_parsed_project(files)` assembles translation units that a caller has
already parsed individually. The x2py CLI uses it after compiler preprocessing
and recipe attachment. Most callers should use `parse_c_project(...)`, which
handles source loading before delegating to the same project assembly path.

## Public API

Implemented top-level and package entrypoints:

```python
from x2py import parse_c_file, parse_c_project
# Equivalent parser-package imports remain available:
# from c_parser import parse_c_file, parse_c_project
```

Implemented signatures:

```python
parse_c_file(
    source_or_path,
    filename=None,
    include_dirs=None,
    preprocessing="raw",
    encoding="utf-8",
)

parse_c_project(
    files,
    include_dirs=None,
    preprocessing="raw",
    encoding="utf-8",
)

```

These return typed parser models analogous to the Fortran parser API. The
current partial phase can populate `functions`, `structs`, `unions`, `enums`,
`typedefs`, `variables`, `includes`, `macros`, and metadata `diagnostics`.
Incomplete `struct name;` and `union name;` declarations are concrete
`CStruct`/`CUnion` types with `is_incomplete=True` and source locations. The
parser returns concrete objects instead of a declaration-kind tag:
`CFunction`, `CVariable`, `CTypedef`, `CStruct`, `CUnion`, and `CEnum`.
A declaration such as
`typedef struct node { int value; } node_t;` produces a `CStruct` plus a
`CTypedef`, while `struct point { int x; } origin;` produces a `CStruct` plus
a `CVariable`.

All types inherit from `CType`. Implemented primitive type classes are
`CVoid`, `CBool`, `CChar`, `CSignedChar`, `CUnsignedChar`, `CShort`,
`CUnsignedShort`, `CInt`, `CUnsignedInt`, `CLong`, `CUnsignedLong`,
`CLongLong`, `CUnsignedLongLong`, `CFloat`, `CDouble`, `CLongDouble`,
`CFloatComplex`, `CDoubleComplex`, and `CLongDoubleComplex`. Qualifiers are
`CConst`, `CVolatile`, `CRestrict`, and `CAtomic`, attached to the precise
type component they qualify. `_Atomic int value;` is stored with a `CAtomic`
qualifier; `_Atomic(int) value;` is represented the same way, while
`_Atomic(int *) value;` qualifies the pointer component. Equivalent primitive orderings, such as
`int unsigned` and `double long`, map to the same concrete type while
invalid combinations, such as `unsigned float`, raise `CParseError` with code
`CPARSE_INVALID_SPECIFIER_SEQUENCE`. A single unresolved typedef-name use remains a `CTypedef`
until resolution can establish whether a matching declaration exists.

Nested declarators are `CComposedType` objects whose `components` are read
from the declared name outward:

```python
int *values[4];       # CComposedType([CArray(bound="4"), CPointer(), CInt()])
int (*matrix)[4];     # CComposedType([CPointer(), CArray(bound="4"), CInt()])
int *(*table)[4];     # CComposedType([CPointer(), CArray(bound="4"), CPointer(), CInt()])
```

`CFunction` has `result_type` and named `CParameter` objects. Its `.type`
property provides the corresponding nameless `CFunctionType`, which is also
used inside pointer typedefs and variables:

```python
int add(int a, int b);     # CFunction(name="add", result_type=CInt(), parameters=[...])
int (*compare)(int, int);  # CVariable(type=CComposedType([CPointer(), CFunctionType(...)]))
```

Function parameters preserve both the written type and C's adjusted callable
type:

```python
void process(int values[4], int callback(int));
# values.declared_type: CComposedType([CArray(bound="4"), CInt()])
# values.type:          CComposedType([CPointer(), CInt()])
# callback.declared_type: CFunctionType(...)
# callback.type:          CComposedType([CPointer(), CFunctionType(...)])
```

Callback-bearing parameters are marked as parser-side callback candidates,
without claiming semantic wrappability. Struct and union `members` are
`CVariable` objects; optional `bit_width` and `initializer` fields preserve
source facts without inventing separate field or valued-variable classes.
Member records carry their own field location. A legal final incomplete array
member in a struct is marked as `CArray(is_flexible=True)`; non-final,
sole-member, and union incomplete-array member forms are retained with
`C_INVALID_FLEXIBLE_ARRAY_MEMBER` error diagnostics.
In compiler/preprocessed mode, common compiler declaration syntax is normalized
before grammar parsing.
Harmless attributes are accepted without dropping their declarations. Ignored
extensions that can affect layout, calling convention, symbol identity, or type
identity produce `C_UNMODELED_COMPILER_EXTENSION` warnings with explicit
`unit_kind` values. Static assertions remain diagnostic-only. Grammar-invalid
input raises `CParseError`; identifier spellings are not used to guess that
input belongs to another language.
Unconsumed declarator suffixes are also diagnosed instead of producing partial
objects. Functions
include `prototype_style`, currently `"prototype"` for
typed or explicit `void` parameter lists and `"unspecified"` for empty
parameter lists such as `int f()`. Function definitions do not store
executable body text; they include direct `start` and `end` locations.
Compatible top-level function redeclarations are merged, and a matching
prototype plus definition prefers the definition while retaining the prototype
location in `declaration_locations`. File-scope tentative variable
declarations such as `int i; int i;` are merged; a later initialized
definition such as `int i = 1;` is preferred over an earlier tentative
declaration. Duplicate initialized variables, duplicate function definitions,
duplicate complete tag definitions, and incompatible top-level redeclarations
produce diagnostics. Local declarations inside function bodies are ignored
because body contents are intentionally skipped.
`x2py` exports the C file/project entrypoints in the same style as the
Fortran entrypoints. The typed C parser package remains importable directly.

Example: parse one header from Python.

```python
from x2py import parse_c_file

parsed = parse_c_file("include/api.h")
print([function.name for function in parsed.functions])
print([typedef.name for typedef in parsed.typedefs])
```

Example: parse a small project with include directories.

```python
from x2py import parse_c_project

project = parse_c_project(["src/api.c", "include/api.h"], include_dirs=["include"])
print(project.include_graph)
print(project.header_source_pairs)
```

Example: parse compiler-preprocessed text produced by the shared x2py CLI.

```bash
python -m x2py include/api.h --language c --parse --json \
  --preprocess compiler \
  --compiler clang-18 \
  -I include \
  -D API_EXPORT=
```

Project-level facts require `parse_c_project(...)`, not just
`parse_c_file(...)`. A single file can report its own raw directives, includes,
macros, declarations, diagnostics, and unresolved typedef/tag references. A
project parse sees multiple files together and can populate include graphs,
system include records, unresolved include sets, functions by file, enum
constants, likely header/source pairs, and basic cross-file typedef/tag links.
An include edge is metadata only: a resolved local or system header is not
parsed unless it is also supplied as a project input or falls beneath a
directory input. Generated headers and direct `.i` streams follow that same
explicit-input rule. Include-graph keys use project input/path identity; they
are not module keys.

When raw input declares incompatible versions of the same function in
alternative `#if`/`#else` branches, each `CFunction` retains a `condition_set`
such as `{"g1:b0"}` or `{"g1:b1"}`. A `CProject` stores such alternatives in
`conditional_function_variants` rather than claiming that one variant is the
unique `functions` entry. Compiler-preprocessed input contains the selected
configuration and therefore does not need this ambiguity representation.

Raw mode does not evaluate C preprocessor conditionals or expand macros
internally. Compiler mode should receive the already-expanded translation unit
from `x2py.preprocessing`.

The parser itself should stay parse-only. If the C frontend later gains
wrappability assessment, that should live in the semantic layer after C parser
models are converted to semantic IR or edited `.pyi` policy is loaded, matching
the current Fortran and `.pyi` readiness boundary.

## CLI Usage

Explicit C mode:

```bash
x2py path/to/api.h --language c --parse
x2py path/to/api.h --language c --parse --json
x2py path/to/api.h --language c --parse --out report.json
```

There is no separate `--parse-c` alias: `--language c --parse` is the shared
language-selection form. Auto-detection remains deferred: a `.c`, `.h`, or
`.i` input without `--language c` exits with language-selection guidance.
Explicit C input containing syntax that cannot be consumed by the modeled C
grammar raises a fatal parser diagnostic instead of emitting a partial C
interface.

## Current JSON Output

Per-file shape:

```text
{
  "<path>": {
    "filename": "<path>",
    "language": "c",
    "parser_status": "partial",
    "preprocessing": "raw",
    "preprocessing_recipe": "<present only for x2py-generated compiler input>",
    "functions": [
      {
        "name": "run",
        "result_type": {"model": "CInt", "qualifiers": [], "source_text": "int"},
        "parameters": [],
        "storage": [],
        "specifiers": [],
        "is_variadic": false,
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
    "variables": [],
    "macros": [],
    "includes": [],
    "diagnostics": []
  }
}
```

JSON compatibility rules:

- prefer additive schema changes
- serialize concrete `CType` identity using `"model"`; reserve `"type"` for
  actual type relationships such as `CTypedef.type`
- serialize qualifier objects as canonical spellings such as `"const"`
- include `source_location` for declaration/directive records and `location`
  for diagnostics
- emit references for reused aggregate or typedef objects rather than
  recursive JSON cycles
- preserve unknown or unresolved information rather than dropping it silently
- emit `condition_set` only for retained raw conditional function alternatives,
  and
  emit project `conditional_function_variants` only when a unique function
  index would discard those alternatives
- keep model fields stable enough for golden fixture testing
- document every intentional schema break

## Readiness Boundary

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
non-fatal metadata diagnostics, such as unresolved local includes or macros
that affect declarations but were recorded rather than expanded. K&R-style function
definitions now raise `CParseError` because the current function parser only
models prototype-style declarations and definitions. Invalid primitive
specifier combinations also raise `CParseError`
(`CPARSE_INVALID_SPECIFIER_SEQUENCE`) because their
invalidity does not depend on later typedef resolution. Known unsupported
declaration extensions are diagnosed rather than partially modeled; additional
syntax diagnostics should be added only with focused tests.
Generic grammar rejection uses `CPARSE_INVALID_SYNTAX`. Diagnostic codes are
stable, explicit category identifiers for tests, tools, and documentation. The
shared registry is [`docs/diagnostic_codes.md`](../diagnostic_codes.md).

## Testing Workflow

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
- C semantic readiness tests
- CLI tests
- semantic conversion tests
- `.pyi` generation/parser tests
- fixture/golden parser tests
- error fixture/golden tests
- corpus parse-only tests

The C test area contains active partial-parser/raw-metadata tests, including
parse-only cJSON regression coverage under `tests/parser/c/`. The active tests cover
public entrypoints, empty model serialization, CLI discovery, JSON/output-file
behavior, unsupported C stages, comment stripping, line-continuation folding,
top-level splitting, include collection, simple macro collection, macro-shaped
declaration deferral, raw conditional branch non-selection and provenance,
mutually exclusive function variant retention, macro-dependency metadata,
explicit-input/non-recursive project include behavior, simple declarations,
variables, typedefs, top-level redeclaration diagnostics, recursive declarator
composition, aggregate definitions, members, enums, simple function
prototypes/definitions, function-definition start/end locations, JSON golden
serialization, fatal diagnostic goldens, and project-level callback typedef
resolution. The `json` regression inputs
intentionally retain recoverable diagnostics from unsupported constructs; they
do not claim complete library parsing. A separately pinned/provenanced corpus
target remains deferred without disabling parser tests. Golden comparison tests rewrite their baselines when
`C_PARSER_UPDATE_GOLDENS=1` is set. Future implementation branches should
activate only the tests for the capability they implement.

Useful local checks for the parse-only frontend:

```bash
pytest -q tests/parser/c tests/parser/test_c_standard_type_probe.py tests/parser/test_preprocessing_cli.py tests/parser/test_cli.py tests/parser/test_fortran_type_probe.py tests/semantics tests/pyi
pytest -q
```

### Declaration Coverage Boundary

Active declaration tests currently cover:

- every implemented primitive spelling and selected reordered equivalent
  spellings mapped to their concrete `CType`
- all qualifier objects, storage metadata, simple/braced/designated initializer
  source text, and multiple declarators
- pointer/array precedence, multidimensional arrays, parameter VLA/static
  metadata and pointer adjustment, function-declared callback adjustment,
  function pointers, callback arrays, and functions returning function
  pointers
- functions, variables, typedefs, struct/union members, enums, incomplete
  tags, inline aggregate aliases, anonymous aggregate typedefs, and recursive
  struct pointers
- legal and invalid flexible array members, precise field locations, and
  named/unnamed/zero-width bit-field source facts
- concrete-type JSON serialization, source locations, and cycle-safe aggregate
  references
- `_Atomic int` and `_Atomic(type)` qualifier placement on scalar and pointer
  declaration forms
- tolerance for common GNU/MS declaration extensions, explicit warnings for
  unmodeled ABI-relevant extension semantics, and diagnostics for K&R
  definitions and remaining trailing declarator extensions
- fatal diagnostics for grammar-invalid syntax and invalid primitive-specifier
  combinations while unresolved single typedef-name uses remain deferred

This is enough coverage for the currently implemented subset, not for all C
declarations.

### Missing Implementation With Examples

| Capability | C example | Current parser boundary | Needed behavior |
| --- | --- | --- | --- |
| Typedef/tag resolution | `typedef unsigned long size_t; size_t count(void);` and `struct state { int id; }; void step(struct state *s);` | Basic project parsing links typedef chains and struct/union/enum tag references while preserving unresolved objects when context is absent. | Deepen conflict policy for broader projects; included/generated files are parsed only when supplied as project inputs. |
| Preprocessed declarations | `#define API(ret) ret` followed by `API(int) run(void);` | Raw mode records macro metadata and does not claim the expanded declaration; compiler or `.i` mode parses expanded declarations, maps locations through `#line` markers, and records `origin="preprocessed"`; x2py-generated streams also record their recipe. | Broaden fixture-driven extension and compiler-family coverage. |
| Additional extension families | `int run(void) __attribute__((visibility("default")));` | Common GNU/MS declaration syntax is accepted; ignored ABI-, layout-, symbol-, or type-relevant semantics produce `C_UNMODELED_COMPILER_EXTENSION`. Broader compiler extensions are not modeled. | Add fixture-driven tolerance or a focused diagnostic for each required extension family. |

### Represented With Focused Tests

These forms are represented by the current parser and have dedicated active
regression tests:

```c
const int * const * volatile chain;
```

The current parser creates distinct qualified `CPointer` components for
`chain`, preserving each qualifier on the exact component it qualifies.
Nested declarations such as `struct outer { struct { int x; } inner; };`
build an anonymous `CStruct` used by member `inner`; preprocessed forms retain
mapped nested member locations and `origin="preprocessed"` recursively.
Atomic declarations such as `_Atomic(int *) p;` qualify the pointer component,
while `_Atomic(int) *p;` qualifies the pointed-to integer component.

For an executable maintainer walkthrough of the parser gateway and
preprocessed source path, read
`tests/parser/c/test_c_parser_developer_tutorial.py`.

Fixture layout should be separate from Fortran:

```text
tests/data/c/
  general/
  json/
  tinyexpr/
  linmath/
  nanosvg/
  stb/
  errors/parser/
  corpus/
  scientific/

tests/parser/c/
  fixtures/
    general/
    json/
    errors/
  generate_c_parser_goldens.py
  errors/generate_c_parser_error_goldens.py
```

Parser goldens group same-stem `.c` and `.h` inputs as one project, with the
`.c` translation unit ordered before its header input to mirror compilation;
explicit header dependency groups put included headers before dependent
headers, such as `nanosvg.h` before `nanosvgrast.h`; an input without a
sibling is parsed as a one-file project. Golden filenames use the project
stem, such as `api.json` or `jsmn.json`. Goldens can be regenerated for all
active projects with
`C_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/parser/c/test_c_fixture_suite.py`.
Fatal diagnostic goldens are regenerated with
`C_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/parser/c/test_c_error_fixture_suite.py`.
The standalone generator modules remain available for targeted refreshes.
By policy, a paired project records source-to-header include edges but parses
each supplied `.c`, `.h`, or `.i` member separately; include traversal is not
a parser input-discovery mechanism.

STB is treated as a family of independent single-file libraries: each
top-level `.h` or `.c` input generates its own one-file project golden rather
than being merged into one large project.

The first real-world corpus target should be cJSON, pinned to an exact release
or commit with license and source provenance. cJSON is small enough for early
stabilization while still covering typedef structs, recursive pointers, public
macro declaration wrappers, constants, `const char *` APIs, `size_t`, and
callback hook members. Library files currently under `tests/data/c/json/`,
`tests/data/c/tinyexpr/`, `tests/data/c/linmath/`, and
`tests/data/c/nanosvg/`, plus STB top-level inputs under `tests/data/c/stb/`,
are regression inputs only until corresponding corpus provenance requirements
are met.

## Documentation Set

The C parser documentation lives under:

```text
docs/c_parser/
```

Current C parser documents:

- `c_parser_reference.md`
- `c_parser_architecture.md`
- `c_parser_cli_workflow.md`

Shared project backlog lives in [`../x2py_checklist.md`](../x2py_checklist.md).

Documentation update rule: every C parser implementation change must update
all affected files under `docs/c_parser/` in the same change. This includes
changes to parser behavior, public API, models, CLI output, tests, fixture
workflow, semantic conversion, semantic readiness, or `.pyi` output. Do not
wait for a separate documentation request before updating these docs.
