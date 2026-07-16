"""Phase 1C whole-module wrapper-plan route selection tests."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from tests.wrapper.fortran._support import REPO_ROOT, _compile_native_object, wrapper_source
from x2py.pipeline import build as build_pipeline
from x2py.semantics.models import PYTHON_EXPORTS_METADATA
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.wrapper_codegen import c as wrapper_c
from x2py.wrapper_codegen import generator as wrapper_generator
from x2py.wrapper_codegen import source_printers as wrapper_source_printers


def _completed_module(source: str, *, module_name: str):
    module = parse_pyi_text(source, module_name=module_name)
    complete_semantic_policies(module)
    return module


def test_route_selector_records_forced_plan_route_and_covered_lanes():
    module = _completed_module(
        """
@bind("SCALE")
@native_call([Addr(Arg(0))])
def scale(x: Float64) -> Float64: ...
""",
        module_name="fmath",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
        force_wrapper_plan=True,
    )

    assert decision.owner_path == "fmath"
    assert decision.selected_route == "wrapper-plan"
    assert decision.uses_wrapper_plan is True
    assert decision.covered_lanes == (
        "scalar-inputs",
        "scalar-direct-results",
        "native-call-runtime",
    )
    assert decision.blockers == ()
    assert decision.rollout_eligible is False
    assert decision.rollout_evidence == (
        "tests/wrapper/fortran/scalars/test_verified_baseline.py::"
        "test_fmath_scalar_sources_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/function_calls/test_optional_arguments.py::"
        "test_fixed_optional_scalar_wrapper_plan_route_matches_all_presence_states",
        "tests/wrapper/fortran/function_calls/test_optional_arguments.py::"
        "test_optional_allocatable_scalar_descriptor_distinguishes_omitted_none_and_value",
        "tests/wrapper/fortran/function_calls/test_scalar_writeback_plan.py::"
        "test_scalar_copy_in_out_returns_replacement_through_both_routes",
        "tests/wrapper/fortran/module_state/test_scalar_module_variable_plan.py::"
        "test_whole_scalar_module_variable_behavior_matches_legacy_route",
        "tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::"
        "test_complete_general_source_preserves_namespaces_through_both_routes",
        "tests/wrapper/fortran/runtime_behavior/test_runtime_policies.py::"
        "test_compiled_runtime_policies_release_gil_and_project_native_errors",
        "tests/wrapper/fortran/runtime_behavior/test_runtime_policies.py::"
        "test_pyi_runtime_policies_release_gil_and_project_native_errors",
        "tests/wrapper/fortran/runtime_behavior/test_runtime_recursion.py::test_recursive_native_runtime_calls",
        "tests/wrapper/fortran/scalars/test_scalar_boundary_plan.py::"
        "test_scalar_value_storage_raw_address_out_and_inout_match_both_routes",
        "tests/wrapper/fortran/scalars/test_scalar_boundary_plan.py::"
        "test_scalar_primitive_kinds_match_both_routes_without_array_blockers",
        "tests/wrapper/fortran/scalars/test_scalar_boundary_plan.py::"
        "test_multiple_scalar_results_match_both_routes_without_array_blockers",
        "tests/wrapper/fortran/strings/test_character_arguments.py::"
        "test_required_scalar_string_inputs_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/strings/test_character_arguments.py::"
        "test_fixed_string_results_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/strings/test_character_edge_cases.py::"
        "test_fixed_hidden_string_output_matches_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/strings/test_character_edge_cases.py::"
        "test_fixed_string_replacement_and_identity_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/strings/test_character_edge_cases.py::"
        "test_assumed_and_optional_string_replacements_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/edit_pyi_contracts/test_native_order_contracts.py::"
        "test_fixed_string_storage_and_raw_address_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/scalars/test_verified_baseline.py::"
        "test_required_array_buffers_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/arrays/test_multidimensional_arrays.py::"
        "test_dense_strided_and_projected_arrays_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/arrays/test_array_results.py::"
        "test_ordinary_array_results_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/arrays/test_assumed_rank_arrays.py::"
        "test_assumed_rank_arrays_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/function_calls/test_optional_arguments.py::"
        "test_optional_array_buffers_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/function_calls/test_output_arguments.py::"
        "test_hidden_ordinary_array_output_matches_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/strings/test_character_arguments.py::"
        "test_fixed_width_character_arrays_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/edit_pyi_contracts/test_native_order_contracts.py::"
        "test_raw_array_addresses_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/edit_pyi_contracts/test_native_order_contracts.py::"
        "test_copy_f_preserves_logical_axes_through_binding_owned_temporary",
        "tests/wrapper/fortran/strings/test_character_arguments.py::"
        "test_raw_fixed_width_character_arrays_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/derived_types/test_pointers.py::"
        "test_module_native_array_handles_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/function_calls/test_optional_arguments.py::"
        "test_optional_array_descriptors_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/module_state/test_allocatable_replacement.py::"
        "test_projected_allocatable_descriptor_matches_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/arrays/test_array_results.py::"
        "test_owned_allocatable_results_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/arrays/test_array_results.py::"
        "test_array_results_follow_data_buffer_and_descriptor_handle_contracts",
        "tests/wrapper/fortran/scalars/test_scalar_boundary_plan.py::"
        "test_scalar_descriptor_results_copy_values_or_none_through_wrapper_plan_route",
        "tests/wrapper/fortran/module_state/test_allocatable_views.py::"
        "test_scalar_descriptor_module_variables_return_copied_optional_values",
        "tests/wrapper/fortran/module_state/test_allocatable_views.py::"
        "test_plain_allocatable_module_array_exposes_current_live_view",
        "tests/wrapper/fortran/strings/test_character_arguments.py::"
        "test_deferred_allocatable_string_results_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/strings/test_character_arguments.py::"
        "test_deferred_character_array_handles_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/derived_types/test_phase8_derived_plan.py::"
        "test_scalar_derived_objects_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/derived_types/test_phase8_derived_plan.py::"
        "test_value_copy_and_optional_derived_inputs_match_source_oracle",
        "tests/wrapper/fortran/derived_types/test_phase8_derived_plan.py::"
        "test_plain_module_derived_proxy_reads_and_writes_live_members",
        "tests/wrapper/fortran/derived_types/test_phase8_derived_plan.py::"
        "test_aliased_module_derived_object_uses_direct_live_field_handles",
        "tests/wrapper/fortran/derived_types/test_phase8_derived_plan.py::"
        "test_derived_module_constant_returns_independent_owned_values",
        "tests/wrapper/fortran/derived_types/test_phase8_derived_plan.py::"
        "test_fixed_string_fields_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/derived_types/test_phase8_derived_plan.py::"
        "test_pointer_field_descriptor_views_match_legacy_and_wrapper_plan_routes",
        "tests/wrapper/fortran/derived_types/test_phase8_derived_plan.py::"
        "test_borrowed_child_retains_owner_and_finalizes_exactly_once",
        "tests/wrapper/fortran/derived_types/test_phase8_derived_plan.py::"
        "test_eligible_derived_contract_selects_production_plan_without_legacy_lowering",
        "tests/wrapper/fortran/derived_types/test_phase9_bound_constructors.py::"
        "test_bound_constructor_replaces_field_initialization_and_reuses_method_plan",
        "tests/wrapper/fortran/naming/test_phase9_class_overloads.py::"
        "test_exact_method_overloads_match_without_trial_calls",
        "tests/wrapper/fortran/naming/test_phase9_class_overloads.py::"
        "test_constructor_overloads_share_owned_allocation_and_exact_matching",
        "tests/wrapper/fortran/callbacks/test_all_callback_shapes.py::"
        "test_immediate_callbacks_cover_all_supported_argument_shapes",
        "tests/wrapper/fortran/callbacks/test_scalar_callbacks.py::"
        "test_callback_exception_prints_traceback_and_aborts_host_process",
    )
    assert decision.selection_reason == "wrapper-plan route forced for internal migration verification"

    rendered = build_pipeline._render_selected_wrapper_plan(module)
    assert rendered.artifacts.module_name == "fmath"
    assert rendered.extension_init_name == "PyInit_fmath"


def test_route_selector_selects_core_scalar_module_for_production_plan_rollout():
    module = _completed_module(
        """
def scale(x: Float64) -> Float64: ...
""",
        module_name="scalar_route_without_parity",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.covered_lanes == (
        "scalar-inputs",
        "scalar-direct-results",
        "native-call-runtime",
    )
    assert decision.blockers == ()
    assert decision.rollout_eligible is True
    assert decision.selection_reason == "whole generation unit is covered by completed wrapper-plan lanes"


@pytest.mark.parametrize(
    ("source", "module_name", "covered_lanes"),
    (
        (
            """
@external
@native_call([Addr(Arg(0)), Addr(Arg(1))])
def optional_value(base: Int32, value: Int32 = ...) -> Int32: ...
""",
            "optional_value",
            (
                "scalar-inputs",
                "scalar-optional-inputs",
                "scalar-direct-results",
                "native-call-runtime",
            ),
        ),
        (
            """
@native_call([Allocatable(Arg(0))])
def descriptor(value: Annotated[Float64, Immutable] | None = ...) -> Int32: ...
""",
            "optional_descriptor",
            (
                "scalar-inputs",
                "scalar-optional-inputs",
                "scalar-descriptor-inputs",
                "scalar-direct-results",
                "native-call-runtime",
            ),
        ),
        (
            'def bump(value: Annotated[Int32, Immutable]) -> Returns["value", Int32]: ...',
            "scalar_writeback",
            ("scalar-inputs", "scalar-writebacks", "native-call-runtime"),
        ),
    ),
)
def test_route_selector_accepts_completed_phase3_scalar_lanes_for_forced_whole_module_parity(
    source: str,
    module_name: str,
    covered_lanes: tuple[str, ...],
):
    module = _completed_module(source, module_name=module_name)

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
        force_wrapper_plan=True,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.covered_lanes == covered_lanes
    assert decision.blockers == ()


@pytest.mark.parametrize(
    ("source", "module_name", "covered_lanes"),
    (
        (
            "def update(value: Float64[()]) -> None: ...",
            "scalar_storage_route",
            ("scalar-storage-inputs", "void-calls", "native-call-runtime"),
        ),
        (
            "def update(value: Addr(Float64)) -> None: ...",
            "scalar_raw_address_route",
            ("scalar-raw-address-inputs", "void-calls", "native-call-runtime"),
        ),
    ),
)
def test_route_selector_accepts_isolated_scalar_address_boundaries(
    source: str,
    module_name: str,
    covered_lanes: tuple[str, ...],
):
    module = _completed_module(source, module_name=module_name)

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
        force_wrapper_plan=True,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.covered_lanes == covered_lanes
    assert decision.blockers == ()


def test_route_selector_selects_completed_scalar_address_boundaries_in_production():
    module = _completed_module(
        """
def update_storage(value: Float64[()]) -> None: ...
def update_raw(value: Addr(Float64)) -> None: ...
""",
        module_name="scalar_address_boundaries",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.rollout_eligible is True
    assert decision.covered_lanes == (
        "scalar-storage-inputs",
        "void-calls",
        "native-call-runtime",
        "scalar-raw-address-inputs",
    )


def test_route_selector_selects_multiple_scalar_results_in_production():
    module = _completed_module(
        """
@native_call([Addr(Arg(0)), Return("status", 1)])
def with_scalar(n: Int32) -> tuple[Int32, Int32]: ...
""",
        module_name="multiple_scalar_results",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.rollout_eligible is True
    assert decision.covered_lanes == (
        "scalar-inputs",
        "scalar-direct-results",
        "scalar-hidden-outputs",
        "scalar-multiple-results",
        "native-call-runtime",
    )


def test_route_selector_accepts_completed_scalar_module_variable_lane():
    module = _completed_module(
        """
limit: Final[Int32] = 12
counter: Int32 = 3
optional_scale: Allocatable[Float64]

def summarize() -> Int32: ...
""",
        module_name="scalar_state",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
        force_wrapper_plan=True,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.covered_lanes == (
        "scalar-direct-results",
        "native-call-runtime",
        "scalar-module-variables",
    )
    assert decision.blockers == ()


def test_route_selector_records_void_call_and_namespace_lanes():
    module = parse_pyi_text(
        """
def ping() -> None: ...
def value(x: Int32) -> Int32: ...
""",
        module_name="namespaced_calls",
    )
    module.functions[1].metadata[PYTHON_EXPORTS_METADATA] = [{"namespace": ("child",), "name": "value"}]
    complete_semantic_policies(module)

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
        force_wrapper_plan=True,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.covered_lanes == (
        "void-calls",
        "native-call-runtime",
        "scalar-inputs",
        "scalar-direct-results",
        "python-namespaces",
    )


def test_route_selector_records_completed_native_status_error_lane():
    module = _completed_module(
        """
@raises(status="status", message="message", success=0)
@native_call([Addr(Arg(0)), Return("status", 0), Return("message", 1)])
def solve(value: Int32) -> tuple[Int32, String[32]]: ...
""",
        module_name="runtime_status",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.rollout_eligible is True
    assert decision.covered_lanes == (
        "scalar-inputs",
        "void-calls",
        "native-call-runtime",
        "native-status-errors",
    )


def test_route_selector_selects_array_buffer_lane_after_native_handle_actuals_are_supported():
    module = _completed_module(
        """
def scale(x: Float64) -> Float64: ...
def sum_values(values: Float64[:]) -> Float64: ...
""",
        module_name="fmath",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.rollout_eligible is True
    assert decision.covered_lanes == (
        "scalar-inputs",
        "scalar-direct-results",
        "native-call-runtime",
        "array-buffer-inputs",
        "array-native-handle-actuals",
    )
    assert decision.blockers == ()
    assert decision.selection_reason == "whole generation unit is covered by completed wrapper-plan lanes"


def test_route_selector_keeps_unimplemented_scalar_kinds_on_legacy_route():
    module = _completed_module(
        "def identity(value: Float128) -> Float128: ...",
        module_name="wide_scalar",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
    )

    assert decision.selected_route == "legacy"
    assert [blocker.reason for blocker in decision.blockers] == [
        "argument 'value' is not a first-lane primitive scalar",
        "result is not a first-lane primitive scalar",
    ]


def test_route_selector_forces_completed_class_units_through_one_plan_route():
    module = _completed_module(
        """
def scale(x: Float64) -> Float64: ...

class sample:
    value: Int32
    def reset(self) -> None: ...
""",
        module_name="fmath",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
        force_wrapper_plan=True,
    )

    assert decision.selected_route == "wrapper-plan"
    assert "class-registration" in decision.covered_lanes
    assert "instance-methods" in decision.covered_lanes
    assert decision.blockers == ()


def test_route_selector_uses_completed_bind_c_direct_symbol_plan():
    module = _completed_module("def add_one(value: Int32) -> Int32: ...", module_name="bind_c_value")
    module.functions[0].metadata["fortran_bind_c"] = True
    module.functions[0].metadata["fortran_bind_c_name"] = "solver_add_one"

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.covered_lanes == (
        "scalar-inputs",
        "scalar-direct-results",
        "native-call-runtime",
    )
    assert decision.blockers == ()


@pytest.mark.parametrize(
    ("source", "module_name", "covered_lanes"),
    (
        (
            "def label(value: String[3]) -> String[3]: ...",
            "fixed_strings",
            ("string-value-inputs", "fixed-string-direct-results", "native-call-runtime"),
        ),
        (
            "def vector() -> Float64[3]: ...",
            "array_result",
            ("array-direct-results", "native-call-runtime"),
        ),
        (
            "@native_call([Return('values', 0)])\ndef hidden() -> Float64[3]: ...",
            "array_hidden_output",
            ("array-hidden-outputs", "native-call-runtime"),
        ),
    ),
)
def test_route_selector_selects_completed_string_and_array_lanes_for_production(
    source: str,
    module_name: str,
    covered_lanes: tuple[str, ...],
):
    module = _completed_module(source, module_name=module_name)

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
    )

    assert decision.selected_route == "wrapper-plan"
    assert decision.rollout_eligible is True
    assert decision.covered_lanes == covered_lanes
    assert decision.blockers == ()


@pytest.mark.parametrize(
    ("source", "module_name", "covered_lanes"),
    (
        (
            'def fill(values: Float64[:]) -> Returns["values", Float64[:]]: ...',
            "array_writeback",
            (
                "array-buffer-inputs",
                "array-native-handle-actuals",
                "array-writebacks",
                "native-call-runtime",
            ),
        ),
        (
            "def maybe(values: Float64[:] = ...) -> None: ...",
            "optional_array",
            (
                "array-buffer-inputs",
                "array-handle-actuals-excluded",
                "array-optional-inputs",
                "void-calls",
                "native-call-runtime",
            ),
        ),
    ),
)
def test_route_selector_uses_phase7_handle_parity_or_keeps_explicit_exclusions_legacy(
    source: str,
    module_name: str,
    covered_lanes: tuple[str, ...],
):
    module = _completed_module(source, module_name=module_name)

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
    )

    expected_route = "legacy" if "array-handle-actuals-excluded" in covered_lanes else "wrapper-plan"
    assert decision.selected_route == expected_route
    assert decision.rollout_eligible is (expected_route == "wrapper-plan")
    assert decision.covered_lanes == covered_lanes
    assert decision.blockers == ()
    if expected_route == "legacy":
        assert decision.selection_reason == "covered lanes exceed the recorded wrapper-plan parity evidence"
    else:
        assert decision.selection_reason == "whole generation unit is covered by completed wrapper-plan lanes"


def test_route_selector_keeps_an_explicitly_forced_legacy_module_entirely_legacy():
    module = _completed_module(
        """
def scale(x: Float64) -> Float64: ...
""",
        module_name="fmath",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
        force_legacy=True,
    )

    assert decision.selected_route == "legacy"
    assert decision.selection_reason == "legacy route forced for migration rollback or comparison"


@pytest.mark.parametrize(
    ("makefile", "strict_wrapper_names"),
    ((True, False), (False, True)),
)
def test_route_selector_reserves_makefile_and_strict_name_modes_for_legacy(
    makefile: bool,
    strict_wrapper_names: bool,
):
    module = _completed_module(
        """
def scale(x: Float64) -> Float64: ...
""",
        module_name="fmath",
    )

    decision = build_pipeline._select_wrapper_plan_route(
        module,
        makefile=makefile,
        strict_wrapper_names=strict_wrapper_names,
    )

    assert decision.selected_route == "legacy"
    assert decision.selection_reason.endswith("mode remains on the legacy route")


def test_route_selector_propagates_plan_construction_failure_without_legacy_retry(monkeypatch):
    module = _completed_module(
        """
def scale(x: Float64) -> Float64: ...
""",
        module_name="fmath",
    )

    class FailingWrapperPlanner:
        def __init__(self, **_kwargs):
            pass

        def build(self, _module):
            raise RuntimeError("planned failure")

    monkeypatch.setattr(build_pipeline, "WrapperPlanner", FailingWrapperPlanner)

    with pytest.raises(RuntimeError, match="planned failure"):
        build_pipeline._render_selected_wrapper_plan(
            module,
        )


def test_source_plan_build_failure_does_not_retry_legacy_lowering(monkeypatch, tmp_path):
    if shutil.which("gfortran") is None:
        pytest.skip("gfortran is required for Fortran wrapper runtime tests")

    def fail_plan_build(*args, **kwargs):
        raise RuntimeError("planned build failure")

    def fail_legacy_lowering(*args, **kwargs):
        raise AssertionError("legacy lowering must not run after plan selection")

    monkeypatch.setattr(build_pipeline, "_build_rendered_wrapper_extension", fail_plan_build)
    monkeypatch.setattr(build_pipeline, "semantic_ir_to_codegen_ast", fail_legacy_lowering)

    with pytest.raises(RuntimeError, match="planned build failure"):
        build_pipeline.build_fortran_extension(
            wrapper_source("fmath.f"),
            output_dir=tmp_path,
            _force_wrapper_plan_route=True,
        )


def test_default_source_plan_construction_failure_does_not_pre_run_legacy_lowering(monkeypatch, tmp_path: Path):
    class FailingWrapperPlanner:
        def __init__(self, **_kwargs):
            pass

        def build(self, _module):
            raise RuntimeError("planned construction failure")

    def fail_legacy_lowering(*args, **kwargs):
        raise AssertionError("legacy lowering must not run for the selected source plan route")

    monkeypatch.setattr(build_pipeline, "WrapperPlanner", FailingWrapperPlanner)
    monkeypatch.setattr(build_pipeline, "semantic_ir_to_codegen_ast", fail_legacy_lowering)

    with pytest.raises(RuntimeError, match="planned construction failure"):
        build_pipeline.build_fortran_extension(
            wrapper_source("fmath.f"),
            output_dir=tmp_path,
        )


def test_source_and_pyi_forced_plan_routes_build_complete_extensions(tmp_path: Path):
    if shutil.which("gfortran") is None:
        pytest.skip("gfortran is required for Fortran wrapper runtime tests")

    source = wrapper_source("fmath.f")
    source_result = build_pipeline.build_fortran_extension(
        source,
        output_dir=tmp_path / "source_build",
        _force_wrapper_plan_route=True,
    )
    native_object = _compile_native_object(source, tmp_path / "native")
    contract = REPO_ROOT / "tests" / "wrapper" / "fortran" / "scalars" / "contracts" / "fmath" / "__init__.pyi"
    pyi_result = build_pipeline.build_pyi_extension(
        contract,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
        _force_wrapper_plan_route=True,
    )

    assert source_result.compiled is True
    assert pyi_result.compiled is True
    assert source_result.module_name == "fmath"
    assert pyi_result.module_name == "fmath"
    assert source_result.shared_library.exists()
    assert pyi_result.shared_library.exists()
    assert pyi_result.manifest is not None
    assert pyi_result.manifest["native_build_plan"] == build_pipeline._manifest_native_plan(
        pyi_result.native_build_plan,
        base=pyi_result.output_dir,
    )


def test_pyi_plan_build_failure_does_not_pre_run_or_retry_legacy_lowering(monkeypatch, tmp_path: Path):
    def fail_plan_build(*args, **kwargs):
        raise RuntimeError("planned build failure")

    def fail_legacy_lowering(*args, **kwargs):
        raise AssertionError("legacy lowering must not run for the selected pyi plan route")

    native_object = tmp_path / "fmath.o"
    native_object.write_text("placeholder native object\n", encoding="utf-8")
    contract = REPO_ROOT / "tests" / "wrapper" / "fortran" / "scalars" / "contracts" / "fmath" / "__init__.pyi"
    monkeypatch.setattr(build_pipeline, "_build_rendered_wrapper_extension", fail_plan_build)
    monkeypatch.setattr(build_pipeline, "semantic_ir_to_codegen_ast", fail_legacy_lowering)

    with pytest.raises(RuntimeError, match="planned build failure"):
        build_pipeline.build_pyi_extension(
            contract,
            native_objects=[native_object],
            output_dir=tmp_path / "build",
            _force_wrapper_plan_route=True,
        )


def test_default_pyi_plan_construction_failure_does_not_pre_run_legacy_lowering(monkeypatch, tmp_path: Path):
    class FailingWrapperPlanner:
        def __init__(self, **_kwargs):
            pass

        def build(self, _module):
            raise RuntimeError("planned construction failure")

    def fail_legacy_lowering(*args, **kwargs):
        raise AssertionError("legacy lowering must not run for the selected pyi plan route")

    native_object = tmp_path / "fmath.o"
    native_object.write_text("placeholder native object\n", encoding="utf-8")
    contract = REPO_ROOT / "tests" / "wrapper" / "fortran" / "scalars" / "contracts" / "fmath" / "__init__.pyi"
    monkeypatch.setattr(build_pipeline, "WrapperPlanner", FailingWrapperPlanner)
    monkeypatch.setattr(build_pipeline, "semantic_ir_to_codegen_ast", fail_legacy_lowering)

    with pytest.raises(RuntimeError, match="planned construction failure"):
        build_pipeline.build_pyi_extension(
            contract,
            native_objects=[native_object],
            output_dir=tmp_path / "build",
        )


def _install_plan_failure_seam(monkeypatch, seam: str, message: str) -> None:
    """Install one named plan-route failure before generated artifacts exist."""
    if seam == "validator":
        monkeypatch.setattr(
            wrapper_generator.WrapperCodeGenerator,
            "_validate_plan",
            lambda _self, _plan: (_ for _ in ()).throw(RuntimeError(message)),
        )
        return
    if seam == "generator":
        monkeypatch.setattr(
            wrapper_c.binding.CBindingGenerator,
            "visit",
            lambda _self, _plan: (_ for _ in ()).throw(RuntimeError(message)),
        )
        return
    if seam == "printer":
        monkeypatch.setattr(
            wrapper_source_printers.CSourcePrinter,
            "doprint",
            lambda _self, _node: (_ for _ in ()).throw(RuntimeError(message)),
        )
        return
    raise AssertionError(f"Unknown plan-route failure seam: {seam}")


def _build_forced_plan_entry(entry: str, tmp_path: Path) -> None:
    """Build one source or contract entry through the forced wrapper-plan route."""
    if entry == "source":
        build_pipeline.build_fortran_extension(
            wrapper_source("fmath.f"),
            output_dir=tmp_path / "source_build",
            _force_wrapper_plan_route=True,
        )
        return
    native_object = tmp_path / "fmath.o"
    native_object.write_text("placeholder native object\n", encoding="utf-8")
    contract = REPO_ROOT / "tests" / "wrapper" / "fortran" / "scalars" / "contracts" / "fmath" / "__init__.pyi"
    build_pipeline.build_pyi_extension(
        contract,
        native_objects=[native_object],
        output_dir=tmp_path / "pyi_build",
        _force_wrapper_plan_route=True,
    )


@pytest.mark.parametrize("entry", ("source", "pyi"))
@pytest.mark.parametrize(
    ("seam", "message"),
    (
        ("validator", "planned validator failure"),
        ("generator", "planned generator failure"),
        ("printer", "planned printer failure"),
    ),
)
def test_selected_plan_failure_seams_do_not_pre_run_or_retry_legacy_lowering(
    monkeypatch,
    tmp_path: Path,
    entry: str,
    seam: str,
    message: str,
):
    if entry == "source" and shutil.which("gfortran") is None:
        pytest.skip("gfortran is required for source-driven wrapper-plan tests")

    def fail_legacy_lowering(*args, **kwargs):
        raise AssertionError(f"legacy lowering must not run for selected {entry} {seam} failure")

    _install_plan_failure_seam(monkeypatch, seam, message)
    monkeypatch.setattr(build_pipeline, "semantic_ir_to_codegen_ast", fail_legacy_lowering)

    with pytest.raises(RuntimeError, match=message):
        _build_forced_plan_entry(entry, tmp_path)
