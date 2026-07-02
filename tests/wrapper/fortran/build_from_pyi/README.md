# Build From `.pyi`

Scope: compiled wrapper builds whose Python API comes from semantic `.pyi`
contracts and whose native implementation comes from explicit native objects,
include/module directories, archives, shared libraries, or named libraries.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/build_from_pyi`

Native data path: `tests/data/fortran/general/` for contract-package runtime
fixtures and `tests/data/fortran/wrapper/` for runtime wrapper fixtures.

Contract fixtures: generated runtime `.pyi` contracts live under
`contracts/<case>/`. Modified and invalid fixtures live under
`modified_contracts/<case>/` and `invalid_contracts/<case>/`.
Generated package expectations that only validate explicit `--pyi --out`
package shape live in `tests/pyi/fixtures/wrapper_contracts/`.

Roadmap items: Stage 1 fixture layout, Stage 2 structured `.pyi` native
artifact plan evidence, single-entry contract discovery, namespace/export
policy, source-free `.pyi` builds, and generated-contract runtime parity
baseline.

Tests: `test_contract_package_runtime.py`, `test_pyi_wrapper_builds.py`.
