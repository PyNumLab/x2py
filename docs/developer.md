# Developer Documentation

This page is for changing x2py. It names the relevant implementation
references, manual commands, focused test files, and fixture generators for each
part of the project.

## References

- [C parser reference](c_parser.md): C frontend scope, preprocessing and
  project policy, parser architecture, CLI behavior, semantic handoff,
  fixtures, and tests.
- [Fortran parser reference](fortran_parser.md): Fortran frontend scope,
  recursive parser organization, API/CLI behavior, diagnostics, fixture
  workflow, semantic handoff, and tests.
- [Semantic IR and `.pyi` reference](semantics.md): shared semantic model,
  datatype policy, `.pyi` loader/printer contract, and C conversion blockers.
- [Wrapper design notes](wrapper_design_notes.md): wrapper-generation policy
  questions intentionally deferred until wrapper implementation.
- [Semantic multilanguage wrapper runtime architecture](architecture/semantic_multilanguage_wrapper_runtime_architecture.md):
  long-term architecture and runtime model.
- [Quality assurance](quality.md): active QA commands, tool benefits, known
  defects found by each tool, and scheduled triage process.

## User-Facing Contract Internals

The user documentation describes CLI stages, `.pyi` syntax, datatype names, and
readiness reports. The developer task is to keep those user-visible contracts
stable, tested, and traceable to implementation files.

### Source Ownership Map

| User-visible area | Main implementation files | Main tests |
| --- | --- | --- |
| Fortran parse output | `fortran_parser/parser.py`, `fortran_parser/models.py`, `fortran_parser/lexer.py` | `tests/parser/test_procedure_and_type_parsing.py`, `tests/parser/test_fortran_fixture_suite.py`, `tests/parser/test_error_handling.py` |
| C parse output | `c_parser/parser.py`, `c_parser/models.py`, `c_parser/lexer.py` | `tests/parser/c/test_c_declarations_and_declarators.py`, `tests/parser/c/test_c_fixture_suite.py`, `tests/parser/c/test_c_error_fixture_suite.py` |
| CLI stage selection and output | `x2py/cli.py`, `fortran_parser/cli.py` | `tests/parser/test_cli.py` |
| Compiler preprocessing | `x2py/preprocessing.py` | `tests/parser/test_preprocessing_cli.py`, `tests/parser/test_preprocessor_and_execution_boundaries.py`, `tests/parser/c/test_c_lexer_preprocessor.py` |
| C standard type probing | `x2py/c_type_probe.py` | `tests/parser/test_c_standard_type_probe.py` |
| Fortran type probing | `x2py/fortran_type_probe.py` | `tests/parser/test_fortran_type_probe.py` |
| Fortran to semantic IR | `semantics/fortran2ir.py`, `semantics/models.py` | `tests/semantics/test_fortran2ir.py` |
| C to semantic IR | `semantics/c2ir.py`, `semantics/models.py` | `tests/semantics/test_c2ir.py`, `tests/semantics/test_c_semantic_readiness.py` |
| `.pyi` printing | `semantics/pyi_printer.py` | `tests/semantics/test_pyi_printer.py`, `tests/semantics/test_pyi_printer_modern_example.py` |
| `.pyi` loading/editing | `semantics/pyi_parser.py` | `tests/pyi/test_pyi_to_ir.py`, `tests/pyi/test_pyi_fixture_suite.py` |
| Readiness reports | `semantics/readiness.py` | `tests/semantics/test_semantic_wrap_readiness.py`, `tests/semantics/test_wrap_readiness_fixture_suite.py` |
| Public API exports | `x2py/__init__.py` | `tests/parser/test_parser_public_entrypoints.py`, `tests/parser/c/test_c_public_api_skeleton.py` |

### `.pyi` Contract Internals

User-visible `.pyi` syntax is parsed by `semantics/pyi_parser.py` and printed
by `semantics/pyi_printer.py`. Both operate on `semantics/models.py`.

Important implementation rules:

- `Ptr(T)` and `Ptr(Const(T))` are storage contracts, not just pretty syntax.
- Array subscriptions such as `Float64[n]` are semantic array contracts.
- `Annotated[..., ORDER_F]`, `ORDER_ANY`, `Allocatable`, `Pointer`, and
  `Intent("out")` are metadata on the semantic storage contract.
- `Final[T]` is the public constant spelling. Do not reintroduce
  `Constant` as user-facing `.pyi` syntax.
- `@native_call` is projection metadata. Use it only when the Python-visible
  signature intentionally differs from the native signature.
- Generated stubs should describe exact native contracts unless semantic IR
  explicitly carries projection metadata.

When changing `.pyi` syntax:

1. Add or update parser tests in `tests/pyi/test_pyi_to_ir.py`.
2. Add or update printer tests in `tests/semantics/test_pyi_printer.py`.
3. Update fixture tests only if the public generated contract changes.
4. Update [user.md](user.md) if users need to write or read the new syntax.
5. Update [semantics.md](semantics.md) for the full reference.

### Datatype Mapping Internals

User-visible datatype names are semantic names, not raw parser spellings.
Mapping happens during parser-to-IR conversion:

- Fortran intrinsic/kind mapping lives in `semantics/fortran2ir.py`.
- C primitive, typedef, and probe-aware mapping lives in `semantics/c2ir.py`.
- The shared dtype names and storage contracts live in `semantics/models.py`.

When changing datatype mapping:

1. Add focused conversion tests in `tests/semantics/test_fortran2ir.py` or
   `tests/semantics/test_c2ir.py`.
2. Add `.pyi` printer/loader coverage if the emitted syntax changes.
3. Update semantic fixtures only when serialized semantic IR intentionally
   changes.
4. Update [user.md](user.md) and [semantics.md](semantics.md) so the visible
   mapping stays accurate.

### Readiness Internals

Readiness is semantic-layer behavior. Parser models should record facts and
diagnostics, but the final `wrappable` answer belongs to
`semantics/readiness.py`.

When adding a readiness blocker:

1. Attach parser-to-IR metadata in `semantics/fortran2ir.py` or
   `semantics/c2ir.py`.
2. Normalize/report it in `semantics/readiness.py`.
3. Add focused tests in `tests/semantics/test_semantic_wrap_readiness.py` or
   `tests/semantics/test_c_semantic_readiness.py`.
4. Update readiness fixtures only if user-visible messages intentionally
   change.
5. Update [user.md](user.md) when the blocker is something users can fix by
   editing `.pyi`.

### Parser To Wrapper Boundary

Do not move wrapper policy into parsers. Parsers can preserve:

- source locations;
- declaration and signature facts;
- type, pointer, array, callback, and aggregate facts;
- preprocessor provenance and diagnostics;
- unresolved references.

Wrappers and semantic readiness decide:

- ownership and lifetime;
- callback registration/unregistration policy;
- output-buffer projection;
- hidden pointer/size projection;
- ABI shim requirements;
- Python-visible signature adaptation.

## Pipeline Internals

The user-facing stages all start in `x2py/cli.py`, but each stage owns a
different layer of the pipeline.

```text
CLI args
  -> language resolution
  -> preprocessing config and source loading
  -> parser models
  -> semantic IR
  -> .pyi printing / .pyi loading
  -> readiness report
```

### CLI And Language Resolution

`x2py/cli.py` is the shared command-line entrypoint. It is responsible for:

- choosing Fortran or C from `--language` and file suffixes;
- rejecting ambiguous directories and unknown suffixes without `--language`;
- building `PreprocessingConfig`;
- dispatching the requested stage flags;
- routing text, JSON, and `--out` output.

Recognizable Fortran files and `.pyi` readiness inputs can omit `--language`.
C files and directories require explicit language selection. Keep this behavior
tested in `tests/parser/test_cli.py` whenever stage selection changes.

The package-specific `fortran_parser/cli.py` remains for the Fortran parser
package entrypoint. New cross-language user behavior normally belongs in
`x2py/cli.py`.

### Preprocessing Internals

`x2py/preprocessing.py` owns compiler-backed preprocessing and provenance. The
main value object is `PreprocessingConfig`; the main execution path is
`run_compiler_preprocessor_with_recipe(...)`.

Important contracts:

- CLI source parsing uses compiler mode. C defaults to `cc`; Fortran defaults
  to `gfortran` unless the user passes a compiler, compile database, or custom
  template.
- C direct parser entrypoints can still be used on raw strings or already
  controlled source in Python tests.
- The preprocessing recipe is part of the parser payload when preprocessing
  happened. It records compiler, adapter, argv, include directories, defines,
  undefs, standard, extra compiler args, included files, source mappings, and
  diagnostics.
- C preprocessing uses GCC/Clang-style `-E -x c` for direct compiler mode.
  Fortran direct compiler mode uses `-E -cpp` plus source-form hints where
  needed.
- Native Fortran `include "..."` is expanded after compiler CPP output because
  it is Fortran textual inclusion, not C/CPP include semantics.

When changing preprocessing behavior, update
`tests/parser/test_preprocessing_cli.py`, source-boundary tests in
`tests/parser/test_preprocessor_and_execution_boundaries.py`, and C raw
directive tests in `tests/parser/c/test_c_lexer_preprocessor.py`.

### Parser Model Internals

Parser models are source facts. They should answer "what did the source say?"
rather than "what Python wrapper should be generated?"

Fortran:

- `fortran_parser/parser.py` slices the file into grammar units, then parses
  each unit's specification region.
- `fortran_parser/models.py` stores `FortranFile`, modules, procedures,
  variables, derived types, interfaces, programs, submodules, and diagnostics.
- Execution bodies are intentionally skipped after the parser has enough
  signature/source facts.

C:

- `c_parser/lexer.py` handles comments, directives, top-level splitting, and
  token source locations.
- `c_parser/parser.py` visits declarations and declarators, records typed
  source facts, and reports unsupported parser-owned syntax.
- `c_parser/models.py` stores functions, variables, typedefs, structs, unions,
  enums, includes, raw directives, preprocessing facts, and diagnostics.

Adding parser fields is a schema decision. Add fields only when downstream
semantic conversion, fixtures, diagnostics, or user-visible behavior need a
new fact.

### Semantic IR Internals

The semantic layer normalizes C and Fortran facts into language-neutral models
from `semantics/models.py`.

- `semantics/fortran2ir.py` maps Fortran procedures, derived types, module
  variables, kinds, shapes, storage contracts, visibility, imported references,
  and compile-time values.
- `semantics/c2ir.py` maps C functions, variables, structs/opaque structs,
  enums, typedef chains, standard-type probe facts, macros, pointer/array
  storage, and C-specific readiness blockers.
- `semantics/pyi_printer.py` emits editable user contracts.
- `semantics/pyi_parser.py` loads edited contracts back into semantic IR.
- `semantics/readiness.py` decides whether that IR is complete enough for
  wrapping.

Keep semantic IR stable where possible. If a parser change does not affect the
semantic contract, avoid changing semantic fixtures.

### `.pyi` Projection Internals

`@native_call` is stored as projection metadata on `SemanticFunction`. The
loader and printer currently support `Arg`, `Return`, `Const`, `Len`,
`IsPresent`, `Work`, and `.shape[...]` value references. They do not currently
implement future wrapper projection helpers such as `Ptr(Arg(...))`, `As[...]`,
status-return policy, ownership conversion, or coercion execution.

The test ownership is:

- loader syntax and error behavior: `tests/pyi/test_pyi_to_ir.py`;
- printer round-trip shape: `tests/semantics/test_pyi_printer.py`;
- readiness interpretation: `tests/semantics/test_semantic_wrap_readiness.py`
  and `tests/semantics/test_c_semantic_readiness.py`.

When adding projection syntax, first add loader tests that prove the accepted
syntax and rejected syntax. Then add printer tests and readiness tests only if
the new metadata affects those layers.

## Testing Strategy

Use the smallest test layer that proves the behavior, then add broader
coverage only when the public contract changes.

### Test Layers

| Layer | Purpose | Typical files |
| --- | --- | --- |
| Focused parser tests | One construct, diagnostic, or model field | `tests/parser/test_*.py`, `tests/parser/c/test_*.py` |
| Parser fixture goldens | Serialized parser contract over curated files | `tests/parser/test_fortran_fixture_suite.py`, `tests/parser/c/test_c_fixture_suite.py` |
| Semantic tests | Parser facts converted to wrapper-neutral IR | `tests/semantics/test_fortran2ir.py`, `tests/semantics/test_c2ir.py` |
| `.pyi` tests | Editable contract loader/printer behavior | `tests/pyi/test_pyi_to_ir.py`, `tests/semantics/test_pyi_printer.py` |
| Readiness tests | User-facing blocker and wrappability decisions | `tests/semantics/test_semantic_wrap_readiness.py`, `tests/semantics/test_c_semantic_readiness.py` |
| CLI tests | User commands, output routing, diagnostics | `tests/parser/test_cli.py`, `tests/parser/test_preprocessing_cli.py` |
| Property/fuzz tests | Broad parser robustness invariants | `tests/property/test_parser_properties.py`, `tests/property/test_semantic_properties.py` |

### Choosing Tests For A Change

- Parser-only source fact: focused parser test first; fixture golden only if
  serialized output changes intentionally.
- CLI flag or output change: CLI test first; update README/user docs if the
  visible command changes.
- New datatype mapping: semantic conversion test plus `.pyi` printer/loader
  tests if emitted syntax changes.
- New `.pyi` syntax: loader test, printer test, readiness test if it resolves
  or creates a blocker.
- New readiness blocker: semantic readiness test and fixture refresh only when
  user-facing messages change.
- Preprocessing behavior: preprocessing CLI tests and at least one parser path
  that consumes the recipe.

### Golden Fixture Rules

Do not regenerate broad fixture sets to hide uncertainty. First write or run a
focused test that explains the intended behavior. Then regenerate only the
affected fixture group when the serialized contract really changed.

Useful commands:

```bash
python tests/parser/c/generate_c_parser_goldens.py tests/data/c/general/math_api.h
python tests/parser/fortran/generate_fortran_parser_goldens.py tests/data/fortran/general/basic_subroutine.f90
python tests/semantics/generate_semantic_fixtures.py
python tests/semantics/generate_wrap_readiness_fixtures.py
python tests/pyi/generate_pyi_fixtures.py
```

### Coverage And CI Parity

When investigating coverage failures, mirror the GitHub Actions coverage flow
instead of relying on a plain local run:

```bash
COVERAGE_PROCESS_START=pyproject.toml PYTHONPATH=. coverage run -m pytest
python -m coverage combine
python -m coverage report
```

The `COVERAGE_PROCESS_START` environment variable matters because subprocess
CLI tests need the same coverage configuration as CI.

## Feature Change Walkthroughs

Use these walkthroughs when adding behavior. They are deliberately procedural:
change the smallest owned layer first, test that layer, then update downstream
contracts only when the public behavior actually changes.

### Add A C Declaration Feature

Example target: support a new declaration spelling or compiler extension in
the C parser.

1. Add the smallest source example to a focused C parser test:
   `tests/parser/c/test_c_declarations_and_declarators.py`,
   `tests/parser/c/test_c_compiler_extensions.py`, or
   `tests/parser/c/test_c_structs_unions_enums_typedefs.py`.
2. Implement the parser change in `c_parser/parser.py`. Add or update model
   fields in `c_parser/models.py` only if the serialized parser contract needs
   new facts.
3. If source splitting or raw directive handling changes, update
   `c_parser/lexer.py` and `tests/parser/c/test_c_lexer_preprocessor.py`.
4. If project-level resolution changes, update
   `tests/parser/c/test_c_project_resolution.py`.
5. If parser JSON changes intentionally, regenerate the relevant project
   golden:

   ```bash
   python tests/parser/c/generate_c_parser_goldens.py tests/data/c/general/math_api.h
   ```

6. If the new parser fact affects semantic conversion, update
   `semantics/c2ir.py` and add coverage in `tests/semantics/test_c2ir.py`.
7. If the generated `.pyi` changes, update `tests/semantics/test_pyi_printer.py`
   or `tests/pyi/test_pyi_fixture_suite.py`.
8. Update [c_parser.md](c_parser.md), [user.md](user.md), or
   [semantics.md](semantics.md) if users or maintainers need to know the new
   behavior.

Focused verification:

```bash
PYTHONPATH=. pytest -q tests/parser/c/test_c_declarations_and_declarators.py
PYTHONPATH=. pytest -q tests/parser/c/test_c_project_resolution.py
PYTHONPATH=. pytest -q tests/semantics/test_c2ir.py
```

### Add A Fortran Parser Feature

Example target: preserve a new declaration attribute, source fact, or argument
metadata item.

1. Add a focused parser test in the file that owns the behavior:
   `tests/parser/test_procedure_and_type_parsing.py`,
   `tests/parser/test_scope_handling.py`, or
   `tests/parser/test_preprocessor_and_execution_boundaries.py`.
2. Implement parsing in `fortran_parser/parser.py`. Add model fields in
   `fortran_parser/models.py` only if the parser output needs to expose the
   new fact.
3. Add parser diagnostic coverage in `tests/parser/test_error_handling.py` if
   malformed source should now fail differently.
4. If project ordering, imports, or compile-time values change, update
   `tests/parser/test_project_scope_models.py` or
   `tests/parser/test_fortran_type_probe.py`.
5. If serialized parser JSON changes intentionally, regenerate the selected
   fixture:

   ```bash
   python tests/parser/fortran/generate_fortran_parser_goldens.py tests/data/fortran/general/basic_subroutine.f90
   ```

6. If the new fact affects semantic output, update `semantics/fortran2ir.py`
   and `tests/semantics/test_fortran2ir.py`.
7. If generated `.pyi` changes, update `tests/semantics/test_pyi_printer.py`
   and the relevant fixture tests.
8. Update [fortran_parser.md](fortran_parser.md), [user.md](user.md), or
   [semantics.md](semantics.md) as needed.

Focused verification:

```bash
PYTHONPATH=. pytest -q tests/parser/test_procedure_and_type_parsing.py
PYTHONPATH=. pytest -q tests/parser/test_fortran_fixture_suite.py
PYTHONPATH=. pytest -q tests/semantics/test_fortran2ir.py
```

### Add Or Change Datatype Mapping

Example target: map a new Fortran kind, C typedef, or target-probed C type.

1. Add conversion coverage in `tests/semantics/test_fortran2ir.py` or
   `tests/semantics/test_c2ir.py`.
2. Implement the mapping in `semantics/fortran2ir.py` or `semantics/c2ir.py`.
3. Keep the public semantic dtype names in `semantics/models.py` stable unless
   there is a deliberate schema decision.
4. If the emitted `.pyi` annotation changes, update
   `tests/semantics/test_pyi_printer.py` and `tests/pyi/test_pyi_to_ir.py`.
5. Update the datatype tables in [user.md](user.md) and [semantics.md](semantics.md).

Focused verification:

```bash
PYTHONPATH=. pytest -q tests/semantics/test_fortran2ir.py tests/semantics/test_c2ir.py
PYTHONPATH=. pytest -q tests/semantics/test_pyi_printer.py tests/pyi/test_pyi_to_ir.py
```

### Add `.pyi` Syntax Or Projection Behavior

Example target: add a new `Annotated[...]` metadata item or projection helper.

1. Add loader tests in `tests/pyi/test_pyi_to_ir.py`.
2. Update `semantics/pyi_parser.py`.
3. Add printer tests in `tests/semantics/test_pyi_printer.py`.
4. Update `semantics/pyi_printer.py`.
5. Update semantic models in `semantics/models.py` only if the IR needs a new
   field or constraint.
6. Update readiness behavior if the new syntax resolves a blocker.
7. Update [user.md](user.md) and [semantics.md](semantics.md).

Focused verification:

```bash
PYTHONPATH=. pytest -q tests/pyi/test_pyi_to_ir.py
PYTHONPATH=. pytest -q tests/semantics/test_pyi_printer.py
PYTHONPATH=. pytest -q tests/semantics/test_semantic_wrap_readiness.py
```

### Add A Readiness Blocker

Example target: report a new unsupported C/Fortran semantic contract clearly.

1. Preserve the source fact in the parser if it is not already present.
2. Attach semantic blocker metadata in `semantics/c2ir.py` or
   `semantics/fortran2ir.py`.
3. Normalize and format the blocker in `semantics/readiness.py`.
4. Add focused readiness tests in
   `tests/semantics/test_semantic_wrap_readiness.py` or
   `tests/semantics/test_c_semantic_readiness.py`.
5. Regenerate readiness message fixtures only when the public message changes:

   ```bash
   python tests/semantics/generate_wrap_readiness_fixtures.py
   ```

6. Update [user.md](user.md) if users can fix the blocker by editing `.pyi`.

Focused verification:

```bash
PYTHONPATH=. pytest -q tests/semantics/test_semantic_wrap_readiness.py
PYTHONPATH=. pytest -q tests/semantics/test_c_semantic_readiness.py
```

### Add Or Change CLI Behavior

Example target: add a stage option, change output routing, or improve
diagnostic formatting.

1. Add CLI tests in `tests/parser/test_cli.py` first.
2. Implement shared dispatch and output behavior in `x2py/cli.py`.
3. Keep Fortran package-specific CLI behavior in `fortran_parser/cli.py`.
4. If compiler preprocessing behavior changes, update `x2py/preprocessing.py`
   and preprocessing tests.
5. Update [user.md](user.md) for user-facing commands and
   [developer.md](developer.md) for maintainer command maps.

Focused verification:

```bash
PYTHONPATH=. pytest -q tests/parser/test_cli.py
PYTHONPATH=. pytest -q tests/parser/test_preprocessing_cli.py
```

## Testing Map

Use this map when changing one part of the project. Each section shows how to
call that part manually, which focused test file to run, and where to look for
more executable examples. Run the broader suite before merging.

### Pre-Merge Checks

Run the full suite from the repository root before merging:

```bash
PYTHONPATH=. pytest -q
```

Run the major suites individually while iterating:

```bash
PYTHONPATH=. pytest -q tests/parser
PYTHONPATH=. pytest -q tests/semantics
PYTHONPATH=. pytest -q tests/pyi
```

As a project policy, do not merge pull requests unless all checks are green.

### Fixture Maintenance

Refresh all C parser project goldens:

```bash
python tests/parser/c/generate_c_parser_goldens.py
```

Refresh one grouped C fixture project:

```bash
python tests/parser/c/generate_c_parser_goldens.py tests/data/c/general/math_api.h
```

Refresh all Fortran parser goldens:

```bash
python tests/parser/fortran/generate_fortran_parser_goldens.py
```

Refresh one Fortran fixture:

```bash
python tests/parser/fortran/generate_fortran_parser_goldens.py tests/data/fortran/general/basic_subroutine.f90
```

In-test Fortran parser fixture update mode:

```bash
FORTRAN_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/parser --confcutdir=tests/
```

Refresh semantic and `.pyi` fixtures:

```bash
python tests/semantics/generate_semantic_fixtures.py
python tests/semantics/generate_wrap_readiness_fixtures.py
python tests/pyi/generate_pyi_fixtures.py
```

When parser model output changes, include the regenerated parser goldens and a
short explanation in the PR. For `.pyi`, semantic IR, or readiness behavior
changes, update the corresponding fixtures under `tests/pyi/fixtures` or
`tests/semantics/fixtures`.

### C Parser

Manual call for one C fixture:

```bash
python -m x2py tests/data/c/general/math_api.h --language c --parse --json
```

Manual Python API call:

```python
from x2py import parse_c_file

parsed = parse_c_file("int add(int a, int b);", filename="example.h")
print([function.name for function in parsed.functions])
```

Focused tests by concern:

- Lexer/preprocessor mechanics:
  `PYTHONPATH=. pytest -q tests/parser/c/test_c_lexer_preprocessor.py`
- Declarations and declarators:
  `PYTHONPATH=. pytest -q tests/parser/c/test_c_declarations_and_declarators.py`
- Functions:
  `PYTHONPATH=. pytest -q tests/parser/c/test_c_functions.py`
- Structs, unions, enums, and typedefs:
  `PYTHONPATH=. pytest -q tests/parser/c/test_c_structs_unions_enums_typedefs.py`
- Project resolution and cross-file facts:
  `PYTHONPATH=. pytest -q tests/parser/c/test_c_project_resolution.py`
- Compiler extensions:
  `PYTHONPATH=. pytest -q tests/parser/c/test_c_compiler_extensions.py`
- Fixture project goldens:
  `PYTHONPATH=. pytest -q tests/parser/c/test_c_fixture_suite.py`
- Fatal parser diagnostics:
  `PYTHONPATH=. pytest -q tests/parser/c/test_c_error_fixture_suite.py`

Regenerate one grouped C fixture project:

```bash
python tests/parser/c/generate_c_parser_goldens.py tests/data/c/general/math_api.h
```

Executable tutorial: `tests/parser/c/test_c_parser_developer_tutorial.py`.

### Fortran Parser

Manual call for one Fortran fixture:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --language fortran --parse --json
```

Manual Python API call:

```python
from x2py import parse_fortran_file

parsed = parse_fortran_file(
    "tests/data/fortran/general/basic_subroutine.f90",
)
print([module.name for module in parsed.modules])
```

Focused tests by concern:

- Parser walkthrough:
  `PYTHONPATH=. pytest -q tests/parser/test_parser_developer_tutorial.py`
- Procedures, declarations, derived types, and interfaces:
  `PYTHONPATH=. pytest -q tests/parser/test_procedure_and_type_parsing.py`
- Scope and project behavior:
  `PYTHONPATH=. pytest -q tests/parser/test_scope_handling.py tests/parser/test_project_scope_models.py`
- Preprocessing and execution-boundary behavior:
  `PYTHONPATH=. pytest -q tests/parser/test_preprocessor_and_execution_boundaries.py`
- Parser diagnostics:
  `PYTHONPATH=. pytest -q tests/parser/test_error_handling.py`
- Fixture goldens:
  `PYTHONPATH=. pytest -q tests/parser/test_fortran_fixture_suite.py`
- Parser error fixtures:
  `PYTHONPATH=. pytest -q tests/parser/test_fortran_error_fixture_suite.py`

Regenerate one Fortran fixture:

```bash
python tests/parser/fortran/generate_fortran_parser_goldens.py tests/data/fortran/general/basic_subroutine.f90
```

Executable tutorial: `tests/parser/test_parser_developer_tutorial.py`.

### Semantics And `.pyi`

Manual calls:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --semantics
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
python -m x2py tests/data/c/general/math_api.h --language c --semantics
python -m x2py tests/data/c/general/math_api.h --language c --pyi
```

Focused tests by concern:

- Fortran parser-to-IR conversion:
  `PYTHONPATH=. pytest -q tests/semantics/test_fortran2ir.py`
- C parser-to-IR conversion:
  `PYTHONPATH=. pytest -q tests/semantics/test_c2ir.py`
- Semantic readiness:
  `PYTHONPATH=. pytest -q tests/semantics/test_semantic_wrap_readiness.py`
- C readiness blockers:
  `PYTHONPATH=. pytest -q tests/semantics/test_c_semantic_readiness.py`
- `.pyi` printer:
  `PYTHONPATH=. pytest -q tests/semantics/test_pyi_printer.py`
- `.pyi` loader and edited stub behavior:
  `PYTHONPATH=. pytest -q tests/pyi/test_pyi_to_ir.py`
- Semantic and `.pyi` fixtures:
  `PYTHONPATH=. pytest -q tests/semantics/test_wrap_readiness_fixture_suite.py tests/pyi/test_pyi_fixture_suite.py`

Regenerate semantic and `.pyi` fixtures:

```bash
python tests/semantics/generate_semantic_fixtures.py
python tests/semantics/generate_wrap_readiness_fixtures.py
python tests/pyi/generate_pyi_fixtures.py
```

Executable examples: `tests/semantics/test_semantic_wrap_readiness.py`,
`tests/semantics/test_pyi_printer.py`, and `tests/pyi/test_pyi_to_ir.py`.

### CLI

Manual calls:

```bash
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --semantics
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
python -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
python -m x2py tests/data/c/general/math_api.h --language c --parse
```

Focused tests:

- Full CLI behavior:
  `PYTHONPATH=. pytest -q tests/parser/test_cli.py`
- Stage dispatch:
  `PYTHONPATH=. pytest -q tests/parser/test_cli.py -k "parse or semantics or pyi or wrap_readiness"`
- Language and preprocessing selection:
  `PYTHONPATH=. pytest -q tests/parser/test_cli.py -k "language or preprocessing"`

Executable reference: `tests/parser/test_cli.py`.
