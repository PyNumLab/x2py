# Test Suite Map

Pytest modules have one primary owner. Unit and stage tests follow the pipeline
and source package that owns the behavior; compiled wrapper tests follow the
user-visible feature that a contributor is changing.

## Pipeline and stage map

| Change area | Test directory | Focused command |
| --- | --- | --- |
| Repository dependency and layout rules | `tests/architecture/` | `python3 -m pytest -q tests/architecture` |
| Command-line behavior | `tests/cli/` | `python3 -m pytest -q tests/cli` |
| C parsing | `tests/parsing/c/` | `python3 -m pytest -q tests/parsing/c` |
| Fortran parsing | `tests/parsing/fortran/` | `python3 -m pytest -q tests/parsing/fortran` |
| Semantic `.pyi` Python-AST parsing | `tests/parsing/pyi/` | `python3 -m pytest -q tests/parsing/pyi` |
| Compiler-derived target facts | `tests/probes/` | `python3 -m pytest -q tests/probes` |
| Preprocessing | `tests/pipeline/preprocessing/` | `python3 -m pytest -q tests/pipeline/preprocessing` |
| Semantic `.pyi` build orchestration | `tests/pipeline/pyi_builds/` | `python3 -m pytest -q tests/pipeline/pyi_builds` |
| C source-to-semantic conversion | `tests/semantics/conversion/c/` | `python3 -m pytest -q tests/semantics/conversion/c` |
| Fortran source-to-semantic conversion | `tests/semantics/conversion/fortran/` | `python3 -m pytest -q tests/semantics/conversion/fortran` |
| `.pyi` AST-to-semantic conversion | `tests/semantics/conversion/pyi/` | `python3 -m pytest -q tests/semantics/conversion/pyi` |
| Completed semantic policy | `tests/semantics/policy/` | `python3 -m pytest -q tests/semantics/policy` |
| Wrap readiness and blockers | `tests/semantics/readiness/` | `python3 -m pytest -q tests/semantics/readiness` |
| Semantic IR-to-codegen lowering | `tests/lowering/` | `python3 -m pytest -q tests/lowering` |
| Bridge generation | `tests/codegen/bridges/` | `python3 -m pytest -q tests/codegen/bridges` |
| Python binding generation | `tests/codegen/bindings/` | `python3 -m pytest -q tests/codegen/bindings` |
| Source and `.pyi` printers | `tests/codegen/printers/` | `python3 -m pytest -q tests/codegen/printers` |
| Naming policy | `tests/naming/` | `python3 -m pytest -q tests/naming` |
| NumPy and semantic type mapping | `tests/types/` | `python3 -m pytest -q tests/types` |
| Runtime handles | `tests/runtime/handles/` | `python3 -m pytest -q tests/runtime/handles` |
| Documentation structure and examples | `tests/docs/` | `python3 -m pytest -q tests/docs` |
| Repository tools | `tests/tools/` | `python3 -m pytest -q tests/tools` |
| Parked performance lane | `tests/benchmarks/` | `python3 -m pytest -q tests/benchmarks` |

Only destinations containing real tests are created. A missing directory in a
checkout means that stage has no dedicated pytest module yet; do not create an
empty directory merely to mirror this table.

## Source-package map

| Source package or surface | Primary test owner |
| --- | --- |
| `x2py.c_parser` | `tests/parsing/c/` |
| `x2py.fortran_parser` | `tests/parsing/fortran/` |
| `x2py.pyi_parser` | `tests/parsing/pyi/` |
| `x2py.probes` | `tests/probes/` |
| `x2py.pipeline` | matching subject under `tests/pipeline/` |
| `x2py.semantics.c2ir`, `fortran2ir`, `pyi2ir` | matching language under `tests/semantics/conversion/` |
| semantic ownership and policy completion | `tests/semantics/policy/` |
| `x2py.semantics.readiness` | `tests/semantics/readiness/` |
| `x2py.semantics.ir2ast` | `tests/lowering/` |
| `x2py.codegen.bridges` | `tests/codegen/bridges/` |
| `x2py.codegen.bindings` | `tests/codegen/bindings/` |
| `x2py.codegen.printers` | `tests/codegen/printers/` |
| `x2py.compiling` | compiled build and runtime feature evidence under `tests/wrapper/fortran/` |
| `x2py.naming` | `tests/naming/` |
| `x2py.types` | `tests/types/` |
| `x2py.runtime.handles` | `tests/runtime/handles/` |
| `x2py.cli` and parser CLIs | `tests/cli/` |
| repository scripts in `tools/` | `tests/tools/` |

## Stage tests versus wrapper feature tests

Stage tests answer “I changed this pipeline stage; which focused suite should I
run?” They should not be filed by roadmap stage number or duplicated with a
stage marker.

Compiled integration/runtime tests answer “I changed this user-visible wrapper
feature; where is its runtime evidence?” They remain feature-oriented under
[`tests/wrapper/fortran/`](wrapper/fortran/README.md). Use
[`tests/wrapper/CHECKLIST_COVERAGE.md`](wrapper/CHECKLIST_COVERAGE.md) when you
know roadmap wording but not the feature module. Source-build,
generated-`.pyi`, and modified-`.pyi` scenarios for one feature stay together;
identical source/generated behavior uses one shared assertion body.

Do not run LAPACK wrapper runtime tests locally. Leave LAPACK coverage to GitHub
Actions unless the task explicitly requests it.

## Adding a test or helper

Add a test to the directory owning the behavior it verifies. A deliberately
cross-stage compiled behavior belongs under `tests/wrapper/`; a build workflow
without feature runtime behavior belongs under `tests/pipeline/`.

Keep a helper in its sole consuming module. Put helpers shared by modules in
the nearest `conftest.py` when they are pytest fixtures/hooks, or `_support.py`
when they are ordinary test utilities. Use `tests/_shared/` only for genuinely
cross-stage utilities; do not make distant tests depend on it for convenience.

Retain orthogonal markers such as `property`, `regression`, `benchmark`, `slow`,
or compiler/tool requirements. Directory ownership replaces stage markers.
