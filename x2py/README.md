# x2py Source Package

This package contains the Python implementation for x2py. Start from the
public behavior you are changing, then follow the owning layer instead of
jumping directly into generated-code internals.

## Main Entry Points

| File or package | Owns |
| --- | --- |
| `cli.py` | User CLI stages, output routing, diagnostics, and wrapper option validation. |
| `wrapping.py` | End-to-end Fortran source and semantic `.pyi` extension builds. |
| `preprocessing.py` | Compiler-backed preprocessing before parser entry. |
| `c_type_probe.py` | C target ABI type facts. |
| `fortran_type_probe.py` | Fortran kind and storage facts. |
| `ownership_policy.py` | Wrapper ownership, transfer, destruction, and codegen action policy. |
| `c_parser/` and `fortran_parser/` | Native source frontends and parser models. |
| `semantics/` | Language-neutral semantic IR, readiness, `.pyi` parsing, and codegen lowering. |
| `codegen/` | Codegen AST, Fortran bridge generation, CPython binding generation, and printers. |
| `compiling/` | Native compiler objects, wrapper compilation, runtime support installation, and linking. |

## Source Navigation Docs

- `docs/developer/source-map.md`
- `docs/developer/feature-to-code-map.md`
- `docs/developer/repository-structure.md`
- `docs/maintainer/internal-architecture/pipeline-map.md`

Keep user-facing support claims in the docs backed by focused tests and, for
wrapper behavior, runtime tests that compile, import, call, mutate, and check
failure paths as applicable.
