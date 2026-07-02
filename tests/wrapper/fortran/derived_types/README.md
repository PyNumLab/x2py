# Derived Types

Scope: derived-type fields, methods, constructors, finalizers, borrowed
children, inheritance, opaque layout boundaries, and pointer behavior tied to
Fortran object lifetimes.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/derived_types`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated derived-type packages live under
`contracts/<case>/` and are refreshed only with `WRAPPER_UPDATE_PYI_FIXTURES=1`.

Roadmap items: Stage 5 generated-contract runtime parity for derived-type
fields, methods, constructors, finalizers, ownership, lifetime, and inheritance
metadata.

Tests: `test_borrowed_finalizers.py`, `test_constructors_and_finalizers.py`,
`test_derived_layout.py`, `test_derived_type_boundaries.py`,
`test_derived_type_generated_pyi_contracts.py`,
`test_derived_type_methods.py`,
`test_inheritance.py`, `test_pointers.py`.
