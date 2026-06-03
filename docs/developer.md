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
