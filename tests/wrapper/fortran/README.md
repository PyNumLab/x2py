# Fortran Wrapper Test Index

Fortran runtime wrapper tests mirror
[`docs/user-guide/fortran-wrapper.md`](../../../docs/user-guide/fortran-wrapper.md)
using feature subjects, not numbered directories. Search for a feature
name, then open its `test_<subject>.py` module and the co-located Fortran fixture.
Shared build/assertion helpers live in `_support.py`.

Tests and fixtures stay flat when each source is wrapped independently. The
`multi_source_builds/` directory is the deliberate exception: each test there
passes several related source files to one wrapper build.

Each feature remains in one pytest module across the three semantic `.pyi`
scenarios:

1. build from Fortran source;
2. build from the generated, unmodified `.pyi` contract; and
3. build from a modified `.pyi` contract.

Source and generated-contract paths should reuse the same behavioral assertion
helpers. Parameterize the imported-module fixture with the `source` and
`generated-pyi` build modes, then pass either result to one test function so
pytest executes the exact same assertion body for both builds. Modified-contract
tests stay in the same feature module but use separate test functions for their
intentional API differences. Shared build-mode fixtures belong in `_support.py`
or `conftest.py`; do not create separate source/generated/modified pytest
modules for one feature.

| Guide subject | Subject tests | Coverage |
| --- | --- | --- |
| Verified baseline | `test_verified_baseline.py` | Fixed/free-form scalar and array builds, calls, mutation, and rejection paths. |
| Generic interfaces | `test_generic_interfaces.py` | Scalar/rank/type overload selection, no-match behavior, and type-bound generics. |
| Defined operators | `test_defined_operators.py` | Arithmetic, unary, relational, reflected, in-place, named operators, assignment, and lifetime. |
| Output arguments | `test_output_arguments.py` | Scalar/array/string/derived outputs, tuple ordering, allocation, mutation, and invalid output arrays. |
| Optional arguments | `test_optional_arguments.py` | Omitted, `None`, positional, keyword, scalar, array, character, derived, output, and inout cases. |
| `value` and `bind(C)` | `test_value_and_bind_c.py` | By-value/by-reference ABI behavior, interoperable kinds, renamed symbols, and shim selection. |
| Allocatable arguments/results | `test_allocatable_views.py`, `test_allocatable_replacement.py` | Copy-return results, borrowed component/module views, replacement, destruction, and Valgrind checks. |
| Pointers | `test_pointers.py` | Call-local inputs, associated/unassociated results, detached snapshots, aliasing, lifetime, and invalid dtype paths. |
| Array-valued results | `test_array_results.py` | Explicit, automatic, allocatable, pointer, zero-sized, multidimensional, rank, order, dtype, and ownership behavior. |
| Array contracts | `test_array_contracts.py`, `test_assumed_rank_arrays.py`, `test_multidimensional_arrays.py`, `test_bind_c_array_type.py` | Assumed-size/rank, lower bounds, shape/order/stride/writeability/alignment/byte-order validation, and zero extents. |
| Derived-type boundaries | `test_derived_type_boundaries.py`, `test_derived_type_methods.py` | Scalar intents/results, nested/private fields, identity/mutation/copy, methods, and borrowed-view lifetime. |
| Inheritance | `test_inheritance.py` | Python inheritance, base layout, overrides, upcasts, polymorphic dispatch, and invalid dynamic types. |
| Constructors/finalizers | `test_constructors_and_finalizers.py`, `test_borrowed_finalizers.py` | Default/keyword construction, failed initialization, exactly-once finalization, and borrowed instances. |
| Module state | `test_module_state.py`, `test_common_blocks.py` | Constants, scalar accessors, mutation visibility, saved/private state, common blocks, and GIL-held accessors. |
| Fortran enums | `test_fortran_enums.py` | Enumerator values, semantic metadata, `Final[...]` stubs, integer surfaces, and runtime round trips. |
| Character behavior | `test_character_arguments.py`, `test_character_edge_cases.py` | Legacy/modern arguments, output/inout copies, lengths, padding/truncation, Unicode, NUL handling, kinds, and blockers. |
| Scalar kinds | `test_scalar_kinds.py` | Integer/logical/real/complex round trips, named kinds, compiler probing, limits, NaN, and infinity. |
| Derived layout | `test_derived_layout.py` | `bind(C)`/`sequence` layout policy, accessors, nested interoperable fields, and by-value copies. |
| Multiple sources and build modes | `multi_source_builds/test_multi_source_builds.py`, `test_build_modes.py`, `test_compiler_verbose.py` | One-extension multi-source builds, caller order, Makefiles, verbose commands, and output placement. |
| Visibility/naming | `test_visibility_naming.py` | Public/private filtering, keywords, collisions, deterministic fixes, and strict errors. |
| Callbacks | `test_scalar_callbacks.py`, `test_array_callbacks.py`, `test_derived_callbacks.py` | Explicit/abstract interfaces, conversions, nested calls, GIL policy, validation, lifetime, and fatal tracebacks. |
| Runtime/concurrency | `test_runtime_policies.py`, `test_runtime_recursion.py`, `test_openmp_runtime.py`, `test_runtime_abi.py` | Error projection, GIL policy, recursion, OpenMP, GNU builds, and debug/optimized ABI behavior. |
| Semantic `.pyi` wrapper builds | `test_pyi_wrapper_builds.py`, `pyi/` | `.pyi` fixtures as wrapper source of truth, generated `.pyi` parity, and native-object link inputs. |

Parser, semantic IR, readiness, and `.pyi` preservation also have narrow tests
in their corresponding suites. The modules indexed here prove that the public
contracts reach generated, compiled, imported wrappers.
