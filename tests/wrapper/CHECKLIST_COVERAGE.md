# Wrapper Checklist Coverage

This file maps the active semantic `.pyi` wrapper roadmap to concrete wrapper
test subjects. Use paths relative to `tests/wrapper/fortran/` so moved test
modules are searchable without relying on old flat filenames.

## Stage 1 — Searchable Layout, Contract Output, And Fixtures

| Roadmap item | Evidence |
| --- | --- |
| Stable top-level subjects | `fortran/build_from_source/README.md`, `fortran/build_from_pyi/README.md`, `fortran/multiple_files/README.md`, `fortran/external_routines/README.md`, `fortran/real_libraries/README.md`, `fortran/edit_pyi_contracts/README.md`, `fortran/arrays/README.md`, `fortran/scalars/README.md`, `fortran/function_calls/README.md`, `fortran/strings/README.md`, `fortran/derived_types/README.md`, `fortran/callbacks/README.md`, `fortran/module_state/README.md`, `fortran/runtime_behavior/README.md`, `fortran/naming/README.md`, `fortran/layout_rules/README.md` |
| Native wrapper fixtures live in shared data corpus | `tests/data/fortran/wrapper/`, `tests/data/fortran/blas/`, `tests/data/fortran/lapack/`, `layout_rules/test_wrapper_guide_layout.py` |
| Runtime contracts live beside consuming subject tests | `build_from_pyi/contracts/runtime_abi/`, `build_from_pyi/modified_contracts/basic_subroutine/flatten_m1.pyi`, `build_from_pyi/modified_contracts/basic_subroutine/alias_increment.pyi`, `build_from_pyi/invalid_contracts/projection_metadata/incomplete_native_call.pyi`, `edit_pyi_contracts/modified_contracts/fnative_call_examples_native_order/fnative_call_examples_f90.pyi`, `edit_pyi_contracts/modified_contracts/fnative_call_examples_immutable/fnative_call_examples_f90.pyi`, `edit_pyi_contracts/modified_contracts/fallocatable_views_explicit_ownership/fallocatable_views_f90.pyi`, `edit_pyi_contracts/modified_contracts/module_variables_visibility/fmodule_vars_f90.pyi`, `layout_rules/test_wrapper_guide_layout.py` |
| Generated wrapper `.pyi` packages are checked fixtures, not tmp-only artifacts | `build_from_pyi/test_pyi_wrapper_builds.py`, `build_from_pyi/test_contract_package_runtime.py`, `build_from_source/test_source_generated_pyi_contracts.py`, `multiple_files/test_multi_source_builds.py`, `external_routines/test_external_procedures.py`, `real_libraries/test_real_blas_lapack.py`, `arrays/test_array_generated_pyi_contracts.py`, `scalars/test_scalar_generated_pyi_contracts.py`, `function_calls/test_function_call_generated_pyi_contracts.py`, `strings/test_string_generated_pyi_contracts.py`, `derived_types/test_derived_type_generated_pyi_contracts.py`, `callbacks/test_callback_generated_pyi_contracts.py`, `module_state/test_module_state_generated_pyi_contracts.py`, `runtime_behavior/test_runtime_behavior_generated_pyi_contracts.py`, `naming/test_naming_generated_pyi_contracts.py`, `tests/pyi/test_contract_package_generation.py` |
| Exact `.pyi` generation-regression suite remains separate | `tests/pyi/fixtures/general/`, `tests/pyi/test_pyi_fixture_suite.py` |
| Subject README and stale-path guard | `layout_rules/test_wrapper_guide_layout.py` |
| Explicit `.pyi` output and single-entry contract behavior | `tests/pyi/test_contract_package_generation.py`, `build_from_pyi/test_contract_package_runtime.py`, `build_from_pyi/test_pyi_wrapper_builds.py` |

## Stage 2 — Structured Native Build Model

| Roadmap item | Evidence |
| --- | --- |
| Structured extension-level native build plan | `build_from_source/test_build_modes.py::test_source_build_result_records_structured_native_plan`, `build_from_pyi/test_pyi_wrapper_builds.py::test_generated_pyi_fixture_builds_from_native_object_without_source_reparse` |
| Ordered link item model across native item kinds | `build_from_source/test_build_modes.py::test_native_link_plan_serializes_interleaved_item_kinds` |
| Lower compiler dependency order preserves caller order | `build_from_source/test_build_modes.py::test_compile_object_dependency_modules_keep_caller_order` |

## Stage 3 — Multi-Source Combined Contract Generation

| Roadmap item | Evidence |
| --- | --- |
| One explicit package for ordered multi-source `--pyi --out` | `multiple_files/test_multi_source_builds.py::test_multi_source_pyi_out_writes_one_flat_combined_package` |
| Source/generated-contract parity with same extension name, namespaces, and link order | `multiple_files/test_multi_source_builds.py::test_multi_source_generated_contract_build_matches_source_runtime_and_link_order` |
| Modified entry export policy while preserving native module children | `multiple_files/test_multi_source_builds.py::test_multi_source_modified_entry_preserves_modules_and_adds_documented_alias` |

## Stage 4 — Shared Parity Harness And Standalone Procedures

| Roadmap item | Evidence |
| --- | --- |
| Shared source/generated fixture pattern for standalone externals | `external_routines/test_external_procedures.py::test_fixed_form_standalone_external_runtime_parity`, `external_routines/test_external_procedures.py::test_free_form_standalone_external_runtime_parity`, `external_routines/test_external_procedures.py::test_one_source_with_several_standalone_externals_exports_each_at_root` |
| Fixed-form, free-form, multi-procedure, and compact BLAS-like external contracts | `external_routines/test_external_procedures.py::test_generated_external_contracts_are_non_empty_root_fragments`, `external_routines/test_external_procedures.py::test_compact_blas_like_folder_generates_one_external_entry_and_preserves_separate_objects` |
| External bridge placement and module-procedure contrast | `external_routines/test_external_procedures.py::test_external_bridge_uses_explicit_interface_and_no_module_use`, `external_routines/test_external_procedures.py::test_module_procedure_bridge_uses_native_module_scope` |
| `@external` with `@bind` and handwritten source-free contracts | `external_routines/test_external_procedures.py::test_external_bind_renames_python_export_without_changing_native_call` |
| C-order flat storage over assumed-size native external buffers | `external_routines/test_external_procedures.py::test_handwritten_c_order_flat_contract_passes_rank_preserving_bridge_view` |
| Invalid root/module placement edits fail before code generation | `external_routines/test_external_procedures.py::test_package_entry_rejects_non_external_root_declaration_before_codegen`, `external_routines/test_external_procedures.py::test_namespace_imported_module_rejects_external_marker_before_codegen` |

## Stage 5 — Full Generated-Contract Runtime Parity

| Roadmap item | Evidence |
| --- | --- |
| Scalar and verified baseline array routines rebuild from generated `.pyi` contracts, expose the same normalized Python names as source builds, compare generated packages against checked fixtures, and use the same runtime assertion bodies | `scalars/test_verified_baseline.py::test_fortran_wrapper_pipeline_builds_importable_extension`, `scalars/test_verified_baseline.py::test_f90_wrapper_pipeline_builds_importable_extension`, `scalars/test_verified_baseline.py::test_fortran_array_wrapper_pipeline_matches_fmath_results_with_contiguous_arrays`, `scalars/test_verified_baseline.py::test_f90_array_wrapper_distinguishes_contiguous_and_strided_contracts`, `scalars/test_fortran_enums.py::test_fortran_enums_preserve_integer_runtime_surface`, `scalars/test_scalar_kinds.py::test_scalar_kind_coverage_uses_compiler_probed_wrapper_types`, `scalars/test_value_and_bind_c.py::test_value_and_existing_bind_c_renamed_symbol_use_correct_abi` |
| Function-call contracts rebuild from generated `.pyi` fixtures with the same optional-argument handling, hidden output projection, multiple-result ordering, allocatable nullable outputs, native-call projection metadata, native shared-library link inputs, and validation failures as source builds | `function_calls/test_optional_arguments.py::test_optional_arguments_accept_missing_and_present_values`, `function_calls/test_optional_arguments.py::test_fixed_form_optional_arguments_support_source_and_generated_contracts`, `function_calls/test_output_arguments.py::test_output_arguments_and_multiple_results_follow_python_projection_rules`, `function_calls/test_native_call_examples.py::test_native_call_examples_cover_scalar_array_string_and_object_projection`, `function_calls/test_native_call_examples.py::test_native_call_examples_build_from_generated_pyi_and_native_shared_library` |
| Array contracts rebuild from generated `.pyi` fixtures with the same dtype, rank, shape, order, stride, lower-bound, writeability, byte-order, alignment, zero-extent, assumed-rank dispatch, and Python-owned result behavior as source builds | `arrays/test_array_contracts.py::test_remaining_array_contracts_are_validated_before_fortran_calls`, `arrays/test_array_results.py::test_array_valued_function_results_are_python_owned_copies`, `arrays/test_assumed_rank_arrays.py::test_assumed_rank_arguments_dispatch_to_runtime_rank`, `arrays/test_assumed_rank_arrays.py::test_assumed_rank_bridge_dispatches_each_runtime_rank_argument`, `arrays/test_multidimensional_arrays.py::test_rank2_contiguous_contract_requires_fortran_contiguous`, `arrays/test_multidimensional_arrays.py::test_rank2_assumed_shape_accepts_fortran_ordered_strided_views`, `arrays/test_multidimensional_arrays.py::test_rank2_assumed_shape_rejects_non_positive_strides`, `arrays/test_multidimensional_arrays.py::test_rank2_explicit_shape_requires_fortran_contiguous`, `arrays/test_multidimensional_arrays.py::test_rank3_contiguous_contract_requires_fortran_contiguous`, `arrays/test_multidimensional_arrays.py::test_rank3_assumed_shape_accepts_fortran_ordered_strided_views` |
| Character contracts rebuild from generated `.pyi` fixtures with the same fixed-length buffers, assumed-length strings, deferred character results, copy-in/copy-out behavior, optional strings, Unicode handling, and embedded-NUL validation as source builds | `strings/test_character_arguments.py::test_legacy_fortran_character_arguments_and_results`, `strings/test_character_arguments.py::test_modern_fortran_character_arguments_and_results`, `strings/test_character_edge_cases.py::test_fortran_character_edge_cases_follow_copy_in_copy_out_policy`, `tests/pyi/test_pyi_to_ir.py::test_native_call_projected_inout_keeps_argument_intent`, `tests/pyi/test_pyi_to_ir.py::test_native_call_projected_output_keeps_explicit_output_intent` |
| Derived-type contracts rebuild from generated `.pyi` fixtures with the same fields, methods, type-bound root targets, constructors, finalizers, borrowed child lifetime, scalar object boundaries, inheritance, polymorphic dispatch, and pointer snapshot behavior as source builds | `derived_types/test_derived_type_methods.py::test_modern_fortran_derived_type_exposes_class_and_type_bound_methods`, `derived_types/test_constructors_and_finalizers.py::test_fortran_default_constructor_keywords_and_finalization`, `derived_types/test_borrowed_finalizers.py::test_borrowed_child_wrapper_never_finalizes_native_component`, `derived_types/test_derived_layout.py::test_bind_c_derived_types_use_accessors_and_fortran_value_copy`, `derived_types/test_derived_type_boundaries.py::test_scalar_derived_types_cross_procedure_boundaries`, `derived_types/test_inheritance.py::test_fortran_extension_types_generate_python_inheritance`, `derived_types/test_pointers.py::test_pointer_arrays_use_call_local_inputs_and_snapshot_results`, `tests/pyi/test_pyi_to_ir.py::test_type_bound_method_declarations_restore_root_target_metadata` |
| Callback contracts rebuild from generated `.pyi` fixtures with the same scalar, array, and derived callback conversions, call-scoped lifetime, GIL entry handling, reference cleanup, and fatal exception behavior as source builds | `callbacks/test_scalar_callbacks.py::test_immediate_scalar_dummy_procedure_calls_python_callback`, `callbacks/test_scalar_callbacks.py::test_callback_exception_prints_traceback_and_aborts_host_process`, `callbacks/test_array_callbacks.py::test_immediate_dummy_procedure_converts_array_arguments_and_results`, `callbacks/test_derived_callbacks.py::test_immediate_dummy_procedure_converts_derived_arguments_and_results`, `tests/pyi/test_pyi_to_ir.py::test_parse_pyi_text_infers_callback_dimension_argument_names` |
| Module-state contracts rebuild from generated `.pyi` fixtures with the same scalar module attributes, parameter behavior, saved native state, allocatable borrowed views, allocatable replacement/copy-return ownership, nullability, and common-block encapsulation as source builds | `module_state/test_module_state.py::test_scalar_module_variables_use_attributes_and_parameters_have_no_native_setter`, `module_state/test_allocatable_views.py::test_allocatable_module_and_derived_type_arrays_are_borrowed_views`, `module_state/test_allocatable_replacement.py::test_allocatable_inout_arrays_are_replaced_with_python_owned_results`, `module_state/test_common_blocks.py::test_common_block_storage_stays_internal_to_wrapped_fortran` |
| Runtime behavior contracts rebuild from generated or edited `.pyi` fixtures with the same recursion/reentrancy behavior, `@hold_gil` GIL policy, `@raises(...)` status projection, and generated wrapper policy code as source-backed builds | `runtime_behavior/test_runtime_recursion.py::test_recursive_native_runtime_calls`, `runtime_behavior/test_runtime_policies.py::test_pyi_runtime_policies_release_gil_and_project_native_errors`, `runtime_behavior/test_runtime_policies.py::test_compiled_runtime_policies_release_gil_and_project_native_errors`, `runtime_behavior/test_openmp_runtime.py::test_openmp_enabled_procedure_builds_with_explicit_gnu_flags` |
| Naming and generic-interface contracts rebuild from generated `.pyi` fixtures with the same public-name normalization, visibility filtering, keyword/collision policy, public generic dispatch, type-bound binding names, defined operators, comparisons, named operators, and assignment behavior as source builds | `naming/test_visibility_naming.py::test_visibility_and_default_python_name_fixing_policy`, `naming/test_generic_interfaces.py::test_fortran_generic_interfaces_dispatch_in_generated_c_extension`, `naming/test_generic_interfaces.py::test_fixed_form_fortran_generic_interface_dispatches_in_generated_c_extension`, `naming/test_defined_operators.py::test_fortran_defined_operators_and_assignment_dispatch_in_generated_c_extension`, `tests/semantics/test_pyi_printer.py::test_fortran_generated_contracts_reserve_colliding_public_names_by_namespace`, `tests/pyi/test_pyi_to_ir.py::test_pyi_codegen_imports_public_generic_not_private_specific_targets`, `tests/pyi/test_pyi_to_ir.py::test_pyi_codegen_keyword_normalized_type_bound_method_uses_native_binding_name` |

## Stage 7 — Library-Scale And Mixed-Bundle Evidence

| Roadmap item | Evidence |
| --- | --- |
| Full real BLAS and LAPACK corpora generate checked contract packages, build full root-procedure wrappers with `build_pyi_extension`, import every root procedure from cached full native shared libraries, and run selected NumPy-style calls against those full modules | `real_libraries/test_real_blas_lapack.py::test_full_library_wrapper_imports_every_root_procedure_from_cached_shared_library` |
| Several contracts imported by one entry resolve from one archive or one shared library while preserving child module namespaces | `real_libraries/test_stage7_native_bundles.py::test_imported_contracts_resolve_from_one_archive_or_shared_library` |
| Module procedures use separately supplied `.mod` directories while standalone `@external` procedures need no module search inputs | `real_libraries/test_stage7_native_bundles.py::test_mixed_module_external_bundle_resolves_all_native_input_kinds`, `real_libraries/test_stage7_native_bundles.py::test_missing_module_directory_reports_compile_error` |
| Mixed native modules and standalone externals expose modules below namespaces and externals at the root while object, archive, direct shared-library, and named-library link items preserve order | `real_libraries/test_stage7_native_bundles.py::test_mixed_module_external_bundle_resolves_all_native_input_kinds` |
| Static archive dependency order, linker archive groups, and required transitive named libraries resolve at runtime | `real_libraries/test_stage7_native_bundles.py::test_static_archive_dependency_order_resolves_transitive_library`, `real_libraries/test_stage7_native_bundles.py::test_static_archive_groups_resolve_cyclic_archive_dependencies`, `real_libraries/test_stage7_native_bundles.py::test_required_transitive_named_library_resolves_runtime_symbol` |
| Missing symbols, duplicate definitions, incompatible artifacts, missing `.mod` directories, and unavailable dependent shared libraries report native diagnostics without source fallback | `real_libraries/test_stage7_native_bundles.py::test_missing_symbol_reports_native_link_or_loader_error`, `real_libraries/test_stage7_native_bundles.py::test_duplicate_native_definitions_report_linker_error`, `real_libraries/test_stage7_native_bundles.py::test_incompatible_native_artifact_reports_linker_error`, `real_libraries/test_stage7_native_bundles.py::test_missing_module_directory_reports_compile_error`, `real_libraries/test_stage7_native_bundles.py::test_unavailable_dependent_shared_library_reports_loader_error` |

## Stage 8 — Editable Contract Semantics

| Roadmap item | Evidence |
| --- | --- |
| Editable native-order contracts can omit `@native_call` when native dummies remain visible, including scalar/array output storage, fixed-length string identity calls with no observable Python `str` mutation, function results, and derived-type output slots | `edit_pyi_contracts/test_native_order_contracts.py::test_editable_contract_can_use_native_order_arguments_without_native_call`, `edit_pyi_contracts/modified_contracts/fnative_call_examples_native_order/fnative_call_examples_f90.pyi` |
| Post-IR immutable replacement policy copies a read-only Python array into mutable native storage and returns a detached replacement without mutating the original object | `edit_pyi_contracts/test_policy_dispatch_contracts.py::test_immutable_array_policy_copies_in_and_returns_replacement`, `edit_pyi_contracts/modified_contracts/fnative_call_examples_immutable/fnative_call_examples_f90.pyi` |
| Immutable writable scalar, string, array, and derived-type arguments use policy-selected native temporaries and return replacements without mutating the original Python-visible object | `edit_pyi_contracts/test_policy_dispatch_contracts.py::test_immutable_scalar_string_array_and_derived_policies_return_replacements`, `edit_pyi_contracts/modified_contracts/fnative_call_examples_immutable_kinds/fnative_call_examples_f90.pyi` |
| Contradictory owner/transfer/destruction triples fail before bridge generation with the declaration and rejected triple in the diagnostic | `edit_pyi_contracts/test_policy_dispatch_contracts.py::test_contradictory_ownership_contract_fails_before_bridge_generation`, `edit_pyi_contracts/invalid_contracts/contradictory_ownership/fnative_call_examples_f90.pyi` |
| Explicit editable ownership triples produce native-owned borrowed module storage, wrapper-owned borrowed component storage, and Python/NumPy-owned copies with distinct release boundaries; borrowed wrapper children retain their owner and finalization runs exactly once | `edit_pyi_contracts/test_ownership_contracts.py`, `edit_pyi_contracts/modified_contracts/fallocatable_views_explicit_ownership/fallocatable_views_f90.pyi`, `edit_pyi_contracts/modified_contracts/fborrowed_finalizer_explicit_ownership/fborrowed_finalizer_f90.pyi` |
| Edited contracts remove classes, methods, constructors, class members, and individual overload candidates; they can also add a renamed `@bind` declaration and a new overload group over existing native specifics | `edit_pyi_contracts/test_surface_edit_contracts.py`, `edit_pyi_contracts/modified_contracts/foverloads_pruned_surface/`, `edit_pyi_contracts/modified_contracts/foverloads_without_constructor_member/`, `edit_pyi_contracts/modified_contracts/foverloads_added_bindings/` |
| Edited `.pyi` contracts can remove a public function and hide declarations with `@private` or `private[...]` while preserving unaffected runtime behavior | `edit_pyi_contracts/test_visibility_contracts.py::test_editable_contract_removes_and_hides_public_declarations`, `edit_pyi_contracts/modified_contracts/module_variables_visibility/fmodule_vars_f90.pyi` |

## Build From Source

- `build_from_source/test_build_modes.py`
- `build_from_source/test_compiler_verbose.py`
- `build_from_source/test_source_generated_pyi_contracts.py`
- `build_from_source/test_runtime_abi.py`

## Build From `.pyi`

- `build_from_pyi/test_contract_package_runtime.py`
- `build_from_pyi/test_pyi_wrapper_builds.py`

## Multiple Files

- `multiple_files/test_multi_source_builds.py`

## External Routines

- `external_routines/test_external_procedures.py`

## Real Libraries

- `real_libraries/test_real_blas_lapack.py`
- `real_libraries/test_stage7_native_bundles.py`

## Edit `.pyi` Contracts

- `edit_pyi_contracts/test_native_order_contracts.py`
- `edit_pyi_contracts/test_ownership_contracts.py`
- `edit_pyi_contracts/test_policy_dispatch_contracts.py`
- `edit_pyi_contracts/test_surface_edit_contracts.py`
- `edit_pyi_contracts/test_visibility_contracts.py`

## Arrays

- `arrays/test_array_contracts.py`
- `arrays/test_array_results.py`
- `arrays/test_assumed_rank_arrays.py`
- `arrays/test_bind_c_array_type.py`
- `arrays/test_array_generated_pyi_contracts.py`
- `arrays/test_multidimensional_arrays.py`

## Scalars

- `scalars/test_fortran_enums.py`
- `scalars/test_scalar_generated_pyi_contracts.py`
- `scalars/test_scalar_kinds.py`
- `scalars/test_value_and_bind_c.py`
- `scalars/test_verified_baseline.py`

## Function Calls

- `function_calls/test_function_call_generated_pyi_contracts.py`
- `function_calls/test_native_call_examples.py`
- `function_calls/test_optional_arguments.py`
- `function_calls/test_output_arguments.py`

## Strings

- `strings/test_character_arguments.py`
- `strings/test_character_edge_cases.py`
- `strings/test_string_generated_pyi_contracts.py`

## Derived Types

- `derived_types/test_borrowed_finalizers.py`
- `derived_types/test_constructors_and_finalizers.py`
- `derived_types/test_derived_layout.py`
- `derived_types/test_derived_type_boundaries.py`
- `derived_types/test_derived_type_methods.py`
- `derived_types/test_derived_type_generated_pyi_contracts.py`
- `derived_types/test_inheritance.py`
- `derived_types/test_pointers.py`

## Callbacks

- `callbacks/test_array_callbacks.py`
- `callbacks/test_derived_callbacks.py`
- `callbacks/test_callback_generated_pyi_contracts.py`
- `callbacks/test_scalar_callbacks.py`

## Module State

- `module_state/test_allocatable_replacement.py`
- `module_state/test_allocatable_views.py`
- `module_state/test_common_blocks.py`
- `module_state/test_module_state_generated_pyi_contracts.py`
- `module_state/test_module_state.py`

## Runtime Behavior

- `runtime_behavior/test_runtime_behavior_generated_pyi_contracts.py`
- `runtime_behavior/test_openmp_runtime.py`
- `runtime_behavior/test_runtime_policies.py`
- `runtime_behavior/test_runtime_recursion.py`

## Naming

- `naming/test_defined_operators.py`
- `naming/test_naming_generated_pyi_contracts.py`
- `naming/test_generic_interfaces.py`
- `naming/test_visibility_naming.py`

## Layout Rules

- `layout_rules/test_codegen_structure.py`
- `layout_rules/test_wrapper_guide_layout.py`
