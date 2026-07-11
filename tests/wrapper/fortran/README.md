# Fortran Wrapper Test Index

Fortran runtime wrapper tests are grouped by plain workflow and behavior names.
Most native Fortran source fixtures live in `tests/data/fortran/wrapper/`; the
real-library subject reads the shared BLAS and LAPACK corpora from
`tests/data/fortran/blas/` and `tests/data/fortran/lapack/`. Runtime semantic
`.pyi` contracts stay beside the tests that consume them.

Generated `.pyi` packages used as runtime wrapper contracts are checked
fixtures. A test that runs `x2py --pyi` for a wrapper runtime scenario compares
the generated package against `contracts/<case>/` before using it. There is no
extra `contracts/generated/` layer; `contracts/` is already the generated
contract fixture root. Modified, handwritten, and invalid contracts use sibling
roots such as
`modified_contracts/<case>/`, `handwritten_contracts/<case>/`, and
`invalid_contracts/<case>/`.
Pure package-shape fixtures that do not compile wrappers live in
`tests/pyi/fixtures/wrapper_contracts/`. Refreshing expected packages is
explicit:

```bash
WRAPPER_UPDATE_PYI_FIXTURES=1 python3 -m pytest -q tests/wrapper/fortran/<subject>
```

| Subject | Scope | Focused pytest command |
| --- | --- | --- |
| `build_from_source/` | Direct Fortran source builds, output placement, verbose compile/link commands, Makefile-adjacent behavior, and ABI build modes. | `python3 -m pytest -q tests/wrapper/fortran/build_from_source` |
| `build_from_pyi/` | Source-free `.pyi` wrapper builds from explicit native artifacts, entry-contract assembly, recursive imports, and namespace/export policy. | `python3 -m pytest -q tests/wrapper/fortran/build_from_pyi` |
| `multiple_files/` | Caller-ordered multi-file builds, generated packages for several files, and modified entry contracts for combined packages. | `python3 -m pytest -q tests/wrapper/fortran/multiple_files` |
| `external_routines/` | Standalone external procedures, root exports, explicit-interface bridges, handwritten external contracts, and flat buffers. | `python3 -m pytest -q tests/wrapper/fortran/external_routines` |
| `real_libraries/` | BLAS/LAPACK-style and mixed-bundle runtime evidence. | `python3 -m pytest -q tests/wrapper/fortran/real_libraries` |
| `edit_pyi_contracts/` | Modified `.pyi` runtime fixtures and edited contract behavior. | `python3 -m pytest -q tests/wrapper/fortran/edit_pyi_contracts` |
| `arrays/` | Array arguments, results, rank/shape/order validation, assumed-rank forms, multidimensional arrays, and `bind(C)` arrays. | `python3 -m pytest -q tests/wrapper/fortran/arrays` |
| `scalars/` | Scalar calls, scalar kind coverage, scalar `bind(C)`/`value`, enum-like values, and the baseline wrapper smoke tests. | `python3 -m pytest -q tests/wrapper/fortran/scalars` |
| `function_calls/` | Optional arguments, output-argument projection, and general Python-callable signature behavior. | `python3 -m pytest -q tests/wrapper/fortran/function_calls` |
| `strings/` | Character arguments, results, fields, fixed/variable-length behavior, and edge cases. | `python3 -m pytest -q tests/wrapper/fortran/strings` |
| `derived_types/` | Derived types, fields, methods, constructors, finalizers, inheritance, layout boundaries, and pointers. | `python3 -m pytest -q tests/wrapper/fortran/derived_types` |
| `callbacks/` | Scalar, array, and derived-type Python callbacks passed to Fortran. | `python3 -m pytest -q tests/wrapper/fortran/callbacks` |
| `module_state/` | Module variables, allocatable state, borrowed views, replacement behavior, and common blocks. | `python3 -m pytest -q tests/wrapper/fortran/module_state` |
| `runtime_behavior/` | Runtime policies, recursion, OpenMP/concurrency evidence, error projection, and GIL policy. | `python3 -m pytest -q tests/wrapper/fortran/runtime_behavior` |
| `naming/` | Public names, visibility, keyword escaping, collision policy, generic interfaces, and defined operators. | `python3 -m pytest -q tests/wrapper/fortran/naming` |
| `layout_rules/` | Wrapper test layout, documentation routing, checklist coverage, fixture placement, and stale-path rejection. | `python3 -m pytest -q tests/wrapper/fortran/layout_rules` |

Run every Fortran wrapper subject with:

```bash
python3 -m pytest -q tests/wrapper/fortran
```

The exact mapping from roadmap items to test paths lives in
[`../CHECKLIST_COVERAGE.md`](../CHECKLIST_COVERAGE.md). Each subject README
lists its native data path, contract fixtures, focused command, and current
roadmap coverage.
