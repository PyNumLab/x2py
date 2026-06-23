# Feature Parity

Scope: compiled runtime behavior for supported Fortran wrapper features,
including scalar calls, arrays, outputs, optional arguments, derived types,
module state, callbacks, runtime policies, and visibility.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/feature_parity`

Native data path: `tests/data/fortran/wrapper/feature_parity/`.

Contract fixtures: none yet; generated and modified runtime `.pyi` parity
fixtures for individual features will be added under `contracts/<case>/` as
Stage 5 and Stage 6 expand.

Roadmap items: Stage 1 subject routing, Stage 4 shared parity harness, Stage 5
generated-contract runtime parity, and Stage 6 editable contract semantics.

Tests: `test_allocatable_replacement.py`, `test_allocatable_views.py`,
`test_array_callbacks.py`, `test_array_contracts.py`, `test_array_results.py`,
`test_assumed_rank_arrays.py`, `test_bind_c_array_type.py`,
`test_borrowed_finalizers.py`, `test_character_arguments.py`,
`test_character_edge_cases.py`, `test_common_blocks.py`,
`test_constructors_and_finalizers.py`, `test_defined_operators.py`,
`test_derived_callbacks.py`, `test_derived_layout.py`,
`test_derived_type_boundaries.py`, `test_derived_type_methods.py`,
`test_fortran_enums.py`, `test_generic_interfaces.py`, `test_inheritance.py`,
`test_module_state.py`, `test_multidimensional_arrays.py`,
`test_openmp_runtime.py`, `test_optional_arguments.py`,
`test_output_arguments.py`, `test_pointers.py`, `test_runtime_policies.py`,
`test_runtime_recursion.py`, `test_scalar_callbacks.py`,
`test_scalar_kinds.py`, `test_value_and_bind_c.py`,
`test_verified_baseline.py`, `test_visibility_naming.py`.
