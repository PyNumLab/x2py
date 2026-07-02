# Edit `.pyi` Contracts

Scope: modified `.pyi` runtime contracts that intentionally alter visibility,
validation, ownership, lifetime, error, projection, or export behavior.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/edit_pyi_contracts`

Native data path: `tests/data/fortran/wrapper/` until dedicated
editable-contract native cases are added.

Contract fixtures: modified editable runtime contracts live under
`modified_contracts/<case>/`. The native-order call case uses
`modified_contracts/fnative_call_examples_native_order/` with the shared
`fnative_call_examples_f90.f90` native fixture. The immutable replacement case
uses `modified_contracts/fnative_call_examples_immutable/` with the same shared
native fixture; `modified_contracts/fnative_call_examples_immutable_kinds/`
extends replacement evidence across scalar, string, array, and derived-type
arguments. The visibility/removal case uses
`modified_contracts/module_variables_visibility/` with the shared
`fmodule_vars_f90.f90` native fixture. The explicit lifetime case uses
`modified_contracts/fallocatable_views_explicit_ownership/` with the shared
`fallocatable_views_f90.f90` native fixture and exercises native-owned,
wrapper-owned, and NumPy-owned array lifetimes in one contract. The matching
wrapper-finalization case uses
`modified_contracts/fborrowed_finalizer_explicit_ownership/` with the shared
`fborrowed_finalizer_f90.f90` fixture. Surface pruning and API addition use the
`foverloads_*` modified contracts with the shared `foverloads_f90.f90` fixture.
Invalid edited contracts live under `invalid_contracts/<case>/`; the
contradictory-ownership case must fail before bridge source is emitted.

Roadmap items: Stage 1 subject routing and Stage 8 editable contract semantics,
including native-order contracts that keep output slots visible without
`@native_call`, even when an ordinary Python `str` cannot observe native
in-place character mutation, and edited contracts that remove or hide public
declarations from the generated Python API.

Tests: `test_native_order_contracts.py`, `test_ownership_contracts.py`,
`test_policy_dispatch_contracts.py`, `test_surface_edit_contracts.py`,
`test_visibility_contracts.py`.
