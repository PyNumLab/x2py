# Contract Generation

Scope: semantic `.pyi` output, entry-contract assembly, recursive relative
imports, namespace preservation, explicit output options, and source-free
`.pyi` wrapper builds from native artifacts.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/contract_generation`

Native data path: `tests/data/fortran/general/` for contract-package generation
fixtures and `tests/data/fortran/wrapper/feature_parity/runtime/` plus
`tests/data/fortran/wrapper/feature_parity/module_state/` for runtime wrapper
fixtures.

Contract fixtures:
`contracts/runtime_abi/generated/fruntime_abi_f90.pyi` is the checked generated
runtime baseline. `contracts/basic_subroutine/modified/flatten_m1.pyi` and
`contracts/basic_subroutine/modified/alias_increment.pyi` record intentional
entry-export edits. `contracts/projection_metadata/invalid/incomplete_native_call.pyi`
is the invalid projection fixture.

Roadmap items: Stage 1 contract fixture layout, Stage 2 structured `.pyi`
native artifact plan evidence, explicit `.pyi` output policy, single-entry
contract discovery, namespace/export policy, and generated-contract runtime
parity baseline.

Tests: `test_contract_package_namespaces.py`, `test_pyi_wrapper_builds.py`.
