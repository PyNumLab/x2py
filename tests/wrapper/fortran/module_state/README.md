# Module State

Scope: Fortran module variables, allocatable module arrays, borrowed views,
replacement behavior, and common blocks.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/module_state`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated module-state packages live under
`contracts/<case>/` and are refreshed only with `WRAPPER_UPDATE_PYI_FIXTURES=1`.

Roadmap items: Stage 5 generated-contract runtime parity for module variables,
allocatable and pointer state, lifetime, nullability, shape, and transfer
contracts.

Tests: `test_allocatable_replacement.py`, `test_allocatable_views.py`,
`test_common_blocks.py`, `test_module_state_generated_pyi_contracts.py`,
`test_module_state.py`.
