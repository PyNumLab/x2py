# Wrapper Checklist Coverage

This file maps the active semantic `.pyi` wrapper roadmap to concrete wrapper
test subjects. Use paths relative to `tests/wrapper/fortran/` so moved test
modules are searchable without relying on old flat filenames.

## Stage 1 — Searchable Layout, Contract Output, And Fixtures

| Roadmap item | Evidence |
| --- | --- |
| Stable top-level subjects | `fortran/contract_generation/README.md`, `fortran/native_build/README.md`, `fortran/multi_source/README.md`, `fortran/standalone/README.md`, `fortran/feature_parity/README.md`, `fortran/editable_contracts/README.md`, `fortran/parity_policy/README.md`, `fortran/library_scale/README.md` |
| Native wrapper fixtures live in shared data corpus | `tests/data/fortran/wrapper/`, `parity_policy/test_wrapper_guide_layout.py` |
| Runtime contracts live beside consuming subject tests | `contract_generation/contracts/runtime_abi/generated/fruntime_abi_f90.pyi`, `contract_generation/contracts/basic_subroutine/modified/flatten_m1.pyi`, `contract_generation/contracts/basic_subroutine/modified/alias_increment.pyi`, `contract_generation/contracts/projection_metadata/invalid/incomplete_native_call.pyi`, `parity_policy/test_wrapper_guide_layout.py` |
| Exact `.pyi` generation-regression suite remains separate | `tests/pyi/fixtures/general/`, `tests/pyi/test_pyi_fixture_suite.py` |
| Subject README and stale-path guard | `parity_policy/test_wrapper_guide_layout.py` |
| Explicit `.pyi` output and single-entry contract behavior | `contract_generation/test_contract_package_namespaces.py`, `contract_generation/test_pyi_wrapper_builds.py` |

## Contract Generation

- `contract_generation/test_contract_package_namespaces.py`
- `contract_generation/test_pyi_wrapper_builds.py`

## Native Build

- `native_build/test_build_modes.py`
- `native_build/test_compiler_verbose.py`
- `native_build/test_runtime_abi.py`

## Multi Source

- `multi_source/test_multi_source_builds.py`

## Standalone

- Current coverage: `multi_source/test_multi_source_builds.py` and `contract_generation/test_contract_package_namespaces.py`
- Dedicated subject tests: planned in Stage 4.

## Feature Parity

- `feature_parity/test_allocatable_replacement.py`
- `feature_parity/test_allocatable_views.py`
- `feature_parity/test_array_callbacks.py`
- `feature_parity/test_array_contracts.py`
- `feature_parity/test_array_results.py`
- `feature_parity/test_assumed_rank_arrays.py`
- `feature_parity/test_bind_c_array_type.py`
- `feature_parity/test_borrowed_finalizers.py`
- `feature_parity/test_character_arguments.py`
- `feature_parity/test_character_edge_cases.py`
- `feature_parity/test_common_blocks.py`
- `feature_parity/test_constructors_and_finalizers.py`
- `feature_parity/test_defined_operators.py`
- `feature_parity/test_derived_callbacks.py`
- `feature_parity/test_derived_layout.py`
- `feature_parity/test_derived_type_boundaries.py`
- `feature_parity/test_derived_type_methods.py`
- `feature_parity/test_fortran_enums.py`
- `feature_parity/test_generic_interfaces.py`
- `feature_parity/test_inheritance.py`
- `feature_parity/test_module_state.py`
- `feature_parity/test_multidimensional_arrays.py`
- `feature_parity/test_openmp_runtime.py`
- `feature_parity/test_optional_arguments.py`
- `feature_parity/test_output_arguments.py`
- `feature_parity/test_pointers.py`
- `feature_parity/test_runtime_policies.py`
- `feature_parity/test_runtime_recursion.py`
- `feature_parity/test_scalar_callbacks.py`
- `feature_parity/test_scalar_kinds.py`
- `feature_parity/test_value_and_bind_c.py`
- `feature_parity/test_verified_baseline.py`
- `feature_parity/test_visibility_naming.py`

## Editable Contracts

- Current coverage: temporary edited-entry assertions in `contract_generation/test_pyi_wrapper_builds.py`
- Dedicated subject tests: planned in Stage 6.

## Parity Policy

- `parity_policy/test_codegen_structure.py`
- `parity_policy/test_wrapper_guide_layout.py`

## Library Scale

- Dedicated subject tests: planned in Stage 8.
