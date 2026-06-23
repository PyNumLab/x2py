# Fortran Wrapper Test Index

Fortran runtime wrapper tests are grouped by stable roadmap subjects. Native
Fortran source fixtures live in `tests/data/fortran/wrapper/`; runtime semantic
`.pyi` contracts stay beside the subject tests that consume them.

| Subject | Scope | Focused pytest command |
| --- | --- | --- |
| `contract_generation/` | Semantic `.pyi` output, entry-contract assembly, recursive imports, namespace policy, and source-free `.pyi` builds. | `python3 -m pytest -q tests/wrapper/fortran/contract_generation` |
| `native_build/` | Direct native build options, output placement, verbose commands, Makefile-adjacent behavior, and ABI build modes. | `python3 -m pytest -q tests/wrapper/fortran/native_build` |
| `multi_source/` | Caller-ordered multi-source builds and generated Makefiles for related source groups. | `python3 -m pytest -q tests/wrapper/fortran/multi_source` |
| `standalone/` | Standalone external-procedure parity expansion. | `python3 -m pytest -q tests/wrapper/fortran/standalone` |
| `feature_parity/` | Runtime behavior for supported wrapper features. | `python3 -m pytest -q tests/wrapper/fortran/feature_parity` |
| `editable_contracts/` | Modified `.pyi` runtime fixtures and edited contract behavior. | `python3 -m pytest -q tests/wrapper/fortran/editable_contracts` |
| `parity_policy/` | Layout, documentation routing, codegen organization, and parity-policy guards. | `python3 -m pytest -q tests/wrapper/fortran/parity_policy` |
| `library_scale/` | BLAS/LAPACK-style and mixed-bundle runtime evidence. | `python3 -m pytest -q tests/wrapper/fortran/library_scale` |

Run every Fortran wrapper subject with:

```bash
python3 -m pytest -q tests/wrapper/fortran
```

The exact mapping from roadmap items to test paths lives in
[`../CHECKLIST_COVERAGE.md`](../CHECKLIST_COVERAGE.md). Each subject README
lists its native data path, contract fixtures, focused command, and current
roadmap coverage.
