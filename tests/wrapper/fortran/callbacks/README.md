# Callbacks

Scope: immediate Python callbacks passed to Fortran, including value,
scalar-storage, array, character-storage, and derived-type callback conversions
and exception behavior.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/callbacks`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated callback packages live under
`contracts/<case>/` and are refreshed only with `WRAPPER_UPDATE_PYI_FIXTURES=1`.

Wrapper-plan route: immediate callback policy is completed before lowering,
then one call-scoped context, C trampoline, and typed Fortran adapter are
generated per callback site. Stored, optional, asynchronous, and cross-thread
callbacks remain blocked.

Roadmap items: Phase 10 direct wrapper-plan parity plus Stage 5
generated-contract runtime parity for callback contracts, call-scoped
lifetime, GIL handling, and conversion behavior.

Tests: `test_all_callback_shapes.py`, `test_array_callbacks.py`,
`test_derived_callbacks.py`, `test_callback_generated_pyi_contracts.py`,
`test_scalar_callbacks.py`.

Structural policy/plan/backend coverage lives in
`tests/wrapper_codegen/test_phase10_callbacks.py`.
