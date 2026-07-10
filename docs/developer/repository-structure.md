---
title: Repository Structure
audience: contributors
prerequisites: repository checkout
related: source-map.md, feature-to-code-map.md, build-system.md, testing-strategy.md
status: maintained
---

# Repository Structure

The repository is a Python project with native fixtures and generated wrapper
artifacts used by tests. Navigate by ownership boundary first, then by file.

## Source Tree

| Path | Purpose |
| --- | --- |
| `x2py/` | Python package implementation. Start with [source-map.md](source-map.md) for entrypoints and [feature-to-code-map.md](feature-to-code-map.md) when starting from behavior. |
| `x2py/contracts/` | Public semantic `.pyi` contract vocabulary imported directly by generated and edited contracts. |
| `x2py/pipeline/` | Shared preprocessing, semantic `.pyi` loading, and high-level wrapper build orchestration. |
| `x2py/probes/` | Compiler-derived target facts and target type mapping reports. |
| `x2py/runtime/` | Python runtime objects used by generated extension modules. |
| `x2py/types/` | Cross-layer mappings from resolved semantic types to Python ecosystem types. |
| `x2py/fortran_parser/` | Fortran parser frontend and Fortran parse report helpers. |
| `x2py/semantics/` | Semantic IR, source-to-IR conversion, `.pyi` parsing, readiness, and codegen lowering. |
| `x2py/compiling/` | Native compile objects, compiler command orchestration, runtime support installation, and linking. |
| `x2py/stdlib/` | Native runtime support copied into generated wrapper builds. |
| `x2py/naming/` | Unified public-name and generated-symbol policy. |
| `x2py/utilities/` | Small shared Python utilities. |

<!-- X2PY_C_DOCS_START
| `x2py/c_parser/` | C parser frontend and C parser CLI helpers. |
| `x2py/codegen/` | Codegen AST models, Fortran bridge generation, CPython binding generation, and printers. |
X2PY_C_DOCS_END -->

The major source packages have local README files under `x2py/` for
developers reading directly in the source tree. Those README files should link
back to the maintained source-navigation docs instead of old top-level docs.

Only `x2py/__init__.py`, `x2py/__main__.py`, and `x2py/cli.py` live directly at
the package root. Public library symbols are deliberately flattened through
`x2py/__init__.py`; internal modules are imported through their owning package.
The one public submodule namespace is `x2py.contracts`, because semantic `.pyi`
files use direct `from x2py.contracts import ...` declarations as part of their
contract syntax.

## Tests

| Path | Purpose |
| --- | --- |
| `tests/parser/` | Parser, preprocessing, CLI, and parser fixture tests. |
| `tests/semantics/` | Semantic IR, readiness, type mapping, and lowering tests. |
| `tests/pyi/` | Semantic `.pyi` parser and fixture tests. |
| `tests/wrapper/fortran/` | Runtime wrapper tests that compile, import, call, and check failure paths. |
| `tests/tools/` | Tooling tests, including documentation example and structure checks. |

<!-- X2PY_C_DOCS_START
| `tests/parser/c/` | C parser-specific tests and fixture maintenance. |
X2PY_C_DOCS_END -->

## Documentation

| Path | Purpose |
| --- | --- |
| `docs/index.md` | Documentation landing page. |
| `docs/user/` | Product workflows, examples, reference, support status, and troubleshooting. |
| `docs/developer/` | Contributor-facing workflows and source navigation. |
| `docs/old_docs/` | Archived pre-reorganization material. Do not link active docs here unless explicitly discussing history. |

## Source Navigation Contract

Source navigation is considered maintained when these files agree:

- [source-map.md](source-map.md): package ownership, hotspot index, and common
  change routes.
- [feature-to-code-map.md](feature-to-code-map.md): user-visible features to
  docs, implementation files, tests, and support evidence.
- `x2py/README.md` and package README files: local entry points for developers
  already browsing the source tree.
- `tests/docs/test_structure.py`: mechanical coverage for the
  navigation pages and README links.

## Generated And Fixture Areas

- `__x2py__/` directories are wrapper build artifacts and should not be
  hand-edited as source.
- Parser and `.pyi` fixture files should be regenerated with the documented
  fixture commands instead of edited loosely.
- `x2py.egg-info/`, caches, and benchmark output are generated local artifacts,
  not source ownership boundaries.

<!-- X2PY_C_DOCS_START
- Native source fixtures live under the shared `tests/data/fortran/` and
  `tests/data/c/` corpora; wrapper runtime tests should reference those shared
  fixtures instead of owning duplicate native sources. Runtime semantic `.pyi`
  contracts stay with the wrapper tests that consume them.
X2PY_C_DOCS_END -->
