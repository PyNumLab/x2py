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
    assert decision.covered_lanes == ("scalar-inputs", "scalar-direct-results")
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
    )
    assert decision.selection_reason == "wrapper-plan route forced for internal migration verification"

    rendered = build_pipeline._render_selected_wrapper_plan(module)
    assert rendered.artifacts.module_name == "fmath"
    assert rendered.extension_init_name == "PyInit_fmath"


def test_route_selector_keeps_core_scalar_module_legacy_while_production_rollout_is_deferred():
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

    assert decision.selected_route == "legacy"
    assert decision.covered_lanes == ("scalar-inputs", "scalar-direct-results")
    assert decision.blockers == ()
    assert decision.rollout_eligible is False
    assert decision.selection_reason == "GIL runtime parity is deferred to Phase 2D"


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
            ("scalar-inputs", "scalar-optional-inputs", "scalar-direct-results"),
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
            ),
        ),
        (
            'def bump(value: Annotated[Int32, Immutable]) -> Returns["value", Int32]: ...',
            "scalar_writeback",
            ("scalar-inputs", "scalar-writebacks"),
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
        "scalar-inputs",
        "scalar-direct-results",
        "python-namespaces",
    )


def test_route_selector_keeps_a_module_with_any_unsupported_member_entirely_legacy():
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

    assert decision.selected_route == "legacy"
    assert decision.rollout_eligible is False
    assert {blocker.owner_path for blocker in decision.blockers} == {"fmath.sum_values"}
    assert decision.selection_reason == "generation unit has unsupported wrapper-plan owners"


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


def test_source_plan_construction_failure_does_not_pre_run_legacy_lowering(monkeypatch, tmp_path: Path):
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
            _force_wrapper_plan_route=True,
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


def test_pyi_plan_construction_failure_does_not_pre_run_legacy_lowering(monkeypatch, tmp_path: Path):
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
            _force_wrapper_plan_route=True,
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
