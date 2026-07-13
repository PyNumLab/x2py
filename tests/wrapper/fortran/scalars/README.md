# Scalars

Scope: scalar calls, scalar kind coverage, `value` and scalar `bind(C)`
behavior, value/storage/raw-address boundaries, scalar output and inout
projection, enum-like values, and the basic compiled-wrapper baseline.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/scalars`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated scalar packages live under
`contracts/<case>/` and are refreshed only with `WRAPPER_UPDATE_PYI_FIXTURES=1`.

Roadmap items: Stage 5 generated-contract runtime parity for scalar ABI types,
kinds, intents, and Python-visible values.

Tests: `test_fortran_enums.py`, `test_scalar_boundary_plan.py`,
`test_scalar_generated_pyi_contracts.py`, `test_scalar_kinds.py`, `test_value_and_bind_c.py`,
`test_verified_baseline.py`.
