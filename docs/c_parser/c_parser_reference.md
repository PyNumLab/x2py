# C Parser Reference

Status: partial parser reference with raw directive metadata. The `c_parser`
package and explicit C CLI parse path exist, raw includes/simple macros are
recorded, and a first grammar-shaped subset parses simple declarations,
typedefs, variables, function prototypes, and function-definition headers with
start/end locations. Incomplete struct/union declarations and basic
struct/union/enum definitions are represented as concrete objects, and
declarators are parsed through a recursive grammar-style path for pointer,
array, function, and parenthesized combinations.

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
- object-like declaration-prefix macro dependencies deferred in raw mode
- raw `#undef` directive provenance in macro metadata
- concrete primitive `CType` objects, pointer/array composition, and concrete
  qualifier objects
- order-insensitive primitive specifier matching with `CPARSE003` errors for
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
- unsupported K&R function-definition diagnostics
- C parser project JSON goldens and fatal diagnostic goldens generated from
  stable `CProject.to_dict()` and `CParseError` output
- C fixture inputs under `tests/data/c/general/`, diagnostic inputs under
  `tests/data/c/errors/parser/`, and partial-parser regression inputs under
  `tests/data/c/json/`, `tests/data/c/tinyexpr/`, `tests/data/c/linmath/`,
  `tests/data/c/nanosvg/`, and top-level C inputs from `tests/data/c/stb/`

Still deferred:

- callback policy metadata beyond parser-side callback candidates
- nested aggregate member definitions and broad compiler-extension declarators
- braced/designated initializer preservation
- cross-declaration and cross-file typedef/tag resolution
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
- record conditional and pragma directives as raw provenance metadata,
  including OpenMP declaration pragmas such as `#pragma omp declare simd` and
  `#pragma omp declare target`
- record function-like macros as metadata with unsupported/deferred diagnostics
- record function-like wrappers and object-like declaration prefixes as
  macro-dependency metadata without claiming they were parsed
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

## Public API

Implemented module-level entrypoints:

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
qualifier; the distinct `_Atomic(int) value;` type-specifier form remains
diagnosed as unsupported. Equivalent primitive orderings, such as
`int unsigned` and `double long`, map to the same concrete type while
invalid combinations, such as `unsigned float`, raise `CParseError` with
code `CPARSE003`. A single unresolved typedef-name use remains a `CTypedef`
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
Selected unsupported forms, such as static assertions,
attributes, alignment specifiers, `_Atomic(type)`, C++-shaped declarations,
and nested aggregate member definitions, are reported in `diagnostics` with
explicit `unit_kind` values.
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
Re-export from `x2py` is still deferred; users should import from `c_parser`.

Project-level facts require `parse_c_project(...)`, not just
`parse_c_file(...)`. A single file can report its own raw directives, includes,
macros, declarations, diagnostics, and unresolved typedef/tag references. A
project parse sees multiple files together and can populate include graphs,
system include records, unresolved include sets, functions by file, enum
constants, likely header/source pairs, and basic cross-file typedef/tag links.

`macro_defines` is reserved for future compiler-assisted preprocessing
configuration. It must not mean that raw mode evaluates C preprocessor
conditionals or expands macros internally.

The parser itself should stay parse-only. If the C frontend later gains
wrappability assessment, that should live in the semantic layer after C parser
models are converted to semantic IR or edited `.pyi` policy is loaded, matching
the current Fortran and `.pyi` readiness boundary.

## CLI Usage

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

## Current JSON Output

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
non-fatal metadata diagnostics, such as unresolved local includes or macros
that affect declarations but were recorded rather than expanded. K&R-style function
definitions now raise `CParseError` because the current function parser only
models prototype-style declarations and definitions. Invalid primitive
specifier combinations also raise `CParseError` (`CPARSE003`) because their
invalidity does not depend on later typedef resolution. Known unsupported
declaration extensions are diagnosed rather than partially modeled; additional
syntax diagnostics should be added only with focused tests.

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

The C test area now contains active partial-parser/raw-metadata tests plus
narrowly scoped roadmap skips under `tests/parser/c/`. The active tests cover
public entrypoints, empty model serialization, CLI discovery, JSON/output-file
behavior, unsupported C stages, comment stripping, line-continuation folding,
top-level splitting, include collection, simple macro collection, macro-shaped
declaration deferral, raw conditional branch non-selection and provenance,
macro-dependency metadata, project include/index behavior, simple declarations,
variables, typedefs, top-level redeclaration diagnostics, recursive declarator
composition, aggregate definitions, members, enums, simple function
prototypes/definitions, function-definition start/end locations, JSON golden
serialization, fatal diagnostic goldens, and project-level callback typedef
resolution. The `json` regression inputs
intentionally retain recoverable diagnostics from unsupported constructs; they
do not claim complete library parsing. Remaining parser-suite skips cover the
pinned/provenanced corpus target and compiler-preprocessed `.i`/`#line`
behavior. Golden comparison tests rewrite their baselines when
`C_PARSER_UPDATE_GOLDENS=1` is set. Future implementation branches should
activate only the tests for the capability they implement, then merge those
branches back into `c-parser/main`.

### Declaration Coverage Boundary

Active declaration tests currently cover:

- every implemented primitive spelling and selected reordered equivalent
  spellings mapped to their concrete `CType`
- all qualifier objects, storage metadata, simple expression initializers, and
  multiple declarators
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
- diagnostics for selected unsupported attributes, alignment, `_Atomic(type)`,
  C++-shaped declarations, nested aggregate definitions, K&R definitions, and
  trailing declarator extensions
- fatal diagnostics for invalid primitive-specifier combinations while
  unresolved single typedef-name uses remain deferred

This is enough coverage for the currently implemented subset, not for all C
declarations.

### Missing Implementation With Examples

| Capability | C example | Current parser boundary | Needed behavior |
| --- | --- | --- | --- |
| Braced/designated initializers | `int values[3] = {1, 2, 3};` and `struct point origin = {.x = 1, .y = 2};` | Simple initializer text such as `int answer = 42;` is preserved; braced forms are not reliably emitted as `CVariable` initializer facts. | Parse or preserve balanced initializer source without treating its braces as an aggregate declaration. |
| Nested aggregate members | `struct outer { struct { int x; } inner; };` | Produces an unsupported-member diagnostic and does not model `inner`. | Build an anonymous `CStruct`/`CUnion` type used by the member variable. |
| Typedef/tag resolution | `typedef unsigned long size_t; size_t count(void);` and `struct state { int id; }; void step(struct state *s);` | Preserves uses as unresolved `CTypedef` or incomplete tag-type objects unless attached inline. | Link uses to declarations across a file/project and diagnose conflicts. |
| Preprocessed declarations | `#define API(ret) ret` followed by `API(int) run(void);` | Raw mode records macro metadata and does not claim the expanded declaration; preprocessed input with line mapping is not implemented. | Accept compiler-expanded input and map each declaration back through `#line` markers. |
| Additional extension families | `int run(void) __attribute__((visibility("default")));` | Known attribute/alignment/`_Atomic(type)` forms are diagnosed; broader compiler extensions are not modeled. | Add fixture-driven support or a focused diagnostic for each required extension family. |

### Represented With Focused Tests

These forms are represented by the current parser and have dedicated active
regression tests:

```c
const int * const * volatile chain;
```

The current parser creates distinct qualified `CPointer` components for
`chain`, preserving each qualifier on the exact component it qualifies.

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
Until include-expanded parsing is implemented, a paired project records the
source-to-header include edge but parses the `.c` and `.h` members separately.

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
