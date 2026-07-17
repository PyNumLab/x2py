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
`test_derived_type_methods.py`, `test_phase8_derived_plan.py`,
`test_scalar_derived_actual_dummy_matrix.py`, `test_inheritance.py`,
`test_phase9_bound_constructors.py`, `test_pointers.py`. Class-owned method and
constructor overload coverage lives with the generic fixture in
`../naming/test_phase9_class_overloads.py`; structural policy/plan validation
lives in `tests/wrapper_codegen/test_phase9_class_surfaces.py`.

The complete scalar-derived actual/dummy matrix has one native source,
`tests/data/fortran/wrapper/fscalar_derived_actual_dummy_matrix_f90.f90`, and
one reduced contract package,
`contracts/fscalar_derived_actual_dummy_matrix_phase8/`. It covers module and
wrapper-owned origins, all six native dummy forms, empty allocatable/pointer
states, holder and module transactions, multi-argument acquisition and
rollback, duplicate-origin validation, qualified types with the same short
name, ordinary/`sequence` typed-value calls, injected cleanup failures,
secondary-compiler ABI smoke coverage, and exact unsupported-cell diagnostics.
It also proves that one call can receive module variables from separate
Fortran modules whose derived types share a short name but have distinct native
identities.
