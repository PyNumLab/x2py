# Runtime Behavior

Scope: runtime policies, recursion, OpenMP/concurrency evidence, error
projection, GIL policy, and compiler/runtime-specific behavior.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/runtime_behavior`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated runtime-policy packages live under
`contracts/<case>/` and are refreshed only with `WRAPPER_UPDATE_PYI_FIXTURES=1`.

Roadmap items: Stage 5 generated-contract runtime parity for runtime policies,
`@hold_gil`, `@raises(...)`, recursion, and concurrency-sensitive behavior.

Tests: `test_runtime_behavior_generated_pyi_contracts.py`,
`test_openmp_runtime.py`, `test_runtime_policies.py`,
`test_runtime_recursion.py`.
