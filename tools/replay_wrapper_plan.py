#!/usr/bin/env python3
"""Retain and verify one maintained dual-route wrapper-plan replay."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import importlib
from pathlib import Path
import sys

from tests.wrapper.fortran._support import _assert_fmath_examples, _compile_native_object, _sole_native_module
from tests.wrapper.fortran.scalars.test_verified_baseline import _scalar_conversion_failure
from x2py.fortran_parser.parser import parse_fortran_project
from x2py.pipeline import build as build_pipeline
from x2py.pipeline.preprocessing import PreprocessingConfig
from x2py.semantics.fortran2ir import fortran_project_to_semantic_modules
from x2py.semantics.policy_completion import complete_semantic_policies

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ReplayUnit:
    """One existing scalar generation unit retained for maintainer replay."""

    source: Path
    contract: Path


_REPLAY_UNITS = {
    "fmath": ReplayUnit(
        source=REPO_ROOT / "tests" / "data" / "fortran" / "wrapper" / "fmath.f",
        contract=(REPO_ROOT / "tests" / "wrapper" / "fortran" / "scalars" / "contracts" / "fmath" / "__init__.pyi"),
    )
}


def replay_wrapper_plan(*, entry: str, unit_name: str, output_dir: Path) -> Path:
    """Replay one maintained source or contract unit through both wrapper routes."""
    unit = _replay_unit(unit_name)
    _prepare_output_directory(output_dir)
    module = _semantic_module(entry, unit)
    legacy_decision = _route_decision(module, force_legacy=True)
    wrapper_plan_decision = _route_decision(module, force_wrapper_plan=True)
    legacy_result, wrapper_plan_result = _build_routes(entry, unit, output_dir)
    _assert_artifact_parity(legacy_result, wrapper_plan_result)
    legacy_module = _import_extension(legacy_result.module_name, legacy_result.output_dir)
    wrapper_plan_module = _import_extension(wrapper_plan_result.module_name, wrapper_plan_result.output_dir)
    _assert_fmath_examples(legacy_module)
    _assert_fmath_examples(wrapper_plan_module)
    _assert_failure_parity(legacy_module, wrapper_plan_module)
    report_path = output_dir / "route-report.txt"
    report_path.write_text(
        _route_report(
            entry=entry,
            unit_name=unit_name,
            output_dir=output_dir,
            legacy_decision=legacy_decision,
            wrapper_plan_decision=wrapper_plan_decision,
            legacy_result=legacy_result,
            wrapper_plan_result=wrapper_plan_result,
        ),
        encoding="utf-8",
    )
    return report_path


def _replay_unit(unit_name: str) -> ReplayUnit:
    """Return one explicitly maintained existing replay unit."""
    try:
        return _REPLAY_UNITS[unit_name]
    except KeyError as exc:
        choices = ", ".join(sorted(_REPLAY_UNITS))
        raise ValueError(f"Unsupported replay unit {unit_name!r}; choose one of: {choices}") from exc


def _prepare_output_directory(output_dir: Path) -> None:
    """Create an empty retained-artifact directory for one deterministic replay."""
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"Replay output directory must be empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)


def _semantic_module(entry: str, unit: ReplayUnit):
    """Build the policy-completed module that the selected replay entry uses."""
    if entry == "source":
        return _source_semantic_module(unit.source)
    if entry == "pyi":
        return _pyi_semantic_module(unit.contract)
    raise ValueError(f"Unsupported replay entry {entry!r}")


def _source_semantic_module(source: Path):
    """Return the merged source-driven semantic module for plan diagnostics."""
    parsed = parse_fortran_project(
        {str(source): build_pipeline._fortran_source_for_pipeline(source, PreprocessingConfig())}
    )
    modules = fortran_project_to_semantic_modules(parsed)
    build_pipeline._apply_source_python_exports(modules)
    module = build_pipeline._merge_wrapper_modules(modules, name=source.stem)
    complete_semantic_policies(module)
    return module


def _pyi_semantic_module(contract: Path):
    """Return the merged semantic-contract module for plan diagnostics."""
    bundle = build_pipeline._pyi_contract_bundle(contract)
    module = build_pipeline._merge_wrapper_modules(
        list(bundle.modules),
        name=build_pipeline._bundle_output_name(bundle),
    )
    complete_semantic_policies(module)
    return module


def _route_decision(module, *, force_legacy: bool = False, force_wrapper_plan: bool = False):
    """Select one explicit route for the retained diagnostic report."""
    return build_pipeline._select_wrapper_plan_route(
        module,
        makefile=False,
        strict_wrapper_names=False,
        force_legacy=force_legacy,
        force_wrapper_plan=force_wrapper_plan,
    )


def _build_routes(entry: str, unit: ReplayUnit, output_dir: Path):
    """Build the retained legacy and wrapper-plan artifact sets for one entry."""
    if entry == "source":
        return _build_source_routes(unit, output_dir)
    return _build_pyi_routes(unit, output_dir)


def _build_source_routes(unit: ReplayUnit, output_dir: Path):
    """Build the existing source fixture through both explicit internal routes."""
    legacy = build_pipeline.build_fortran_extension(
        unit.source,
        output_dir=output_dir / "legacy",
        _force_legacy_wrapper_route=True,
    )
    wrapper_plan = build_pipeline.build_fortran_extension(
        unit.source,
        output_dir=output_dir / "wrapper-plan",
        _force_wrapper_plan_route=True,
    )
    return legacy, wrapper_plan


def _build_pyi_routes(unit: ReplayUnit, output_dir: Path):
    """Build the existing semantic contract through both explicit internal routes."""
    native_object = _compile_native_object(unit.source, output_dir / "native")
    common = {
        "native_objects": (native_object,),
        "native_include_dirs": (native_object.parent,),
    }
    legacy = build_pipeline.build_pyi_extension(
        unit.contract,
        output_dir=output_dir / "legacy",
        _force_legacy_wrapper_route=True,
        **common,
    )
    wrapper_plan = build_pipeline.build_pyi_extension(
        unit.contract,
        output_dir=output_dir / "wrapper-plan",
        _force_wrapper_plan_route=True,
        **common,
    )
    return legacy, wrapper_plan


def _assert_artifact_parity(legacy_result, wrapper_plan_result) -> None:
    """Require both routes to retain the same generated artifact names."""
    legacy_names = tuple(path.name for path in legacy_result.generated_sources)
    wrapper_plan_names = tuple(path.name for path in wrapper_plan_result.generated_sources)
    if legacy_names != wrapper_plan_names:
        raise AssertionError(f"Generated artifact names differ: {legacy_names!r} != {wrapper_plan_names!r}")
    if not legacy_names:
        raise AssertionError("Maintainer replay retained no generated wrapper artifacts")


def _import_extension(module_name: str, output_dir: Path):
    """Import one retained extension without reusing the other route's module."""
    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(output_dir))
    try:
        return _sole_native_module(importlib.import_module(module_name))
    finally:
        sys.path.remove(str(output_dir))


def _assert_failure_parity(legacy_module, wrapper_plan_module) -> None:
    """Reuse the existing conversion failure and recovery assertion for both routes."""
    legacy_failure = _scalar_conversion_failure(legacy_module)
    wrapper_plan_failure = _scalar_conversion_failure(wrapper_plan_module)
    if legacy_failure != wrapper_plan_failure:
        raise AssertionError(f"Scalar conversion failures differ: {legacy_failure!r} != {wrapper_plan_failure!r}")


def _route_report(
    *,
    entry: str,
    unit_name: str,
    output_dir: Path,
    legacy_decision,
    wrapper_plan_decision,
    legacy_result,
    wrapper_plan_result,
) -> str:
    """Render deterministic route, artifact, and build-requirement evidence."""
    lines = [
        f"entry={entry}",
        f"unit={unit_name}",
        *_decision_lines("legacy", legacy_decision),
        *_decision_lines("wrapper-plan", wrapper_plan_decision),
        *_build_lines("legacy", legacy_result, output_dir),
        *_build_lines("wrapper-plan", wrapper_plan_result, output_dir),
        "artifact_names_equal=true",
        "runtime_assertions=passed",
        "conversion_failure_parity=passed",
    ]
    return "\n".join(lines) + "\n"


def _decision_lines(label: str, decision) -> tuple[str, ...]:
    """Return stable recorded fields from one structured pipeline decision."""
    blockers = ",".join(f"{item.owner_path}:{item.reason}" for item in decision.blockers) or "none"
    return (
        f"{label}.owner={decision.owner_path}",
        f"{label}.selected_route={decision.selected_route}",
        f"{label}.covered_lanes={','.join(decision.covered_lanes) or 'none'}",
        f"{label}.rollout_eligible={str(decision.rollout_eligible).lower()}",
        f"{label}.rollout_evidence={','.join(decision.rollout_evidence) or 'none'}",
        f"{label}.selection_reason={decision.selection_reason}",
        f"{label}.blockers={blockers}",
    )


def _build_lines(label: str, result, output_dir: Path) -> tuple[str, ...]:
    """Return stable artifact and native-build requirements for one route."""
    plan = result.native_build_plan
    return (
        f"{label}.module_name={result.module_name}",
        f"{label}.compiled={str(result.compiled).lower()}",
        f"{label}.generated_sources={_paths(result.generated_sources, output_dir)}",
        f"{label}.generated_files={_paths(result.generated_files, output_dir)}",
        f"{label}.native_compilation_units={_paths((unit.source for unit in plan.compilation_units), output_dir)}",
        f"{label}.native_produced_objects={_paths(plan.produced_objects, output_dir)}",
        f"{label}.native_prebuilt_artifacts={_paths((item.path for item in plan.prebuilt_artifacts), output_dir)}",
        f"{label}.native_link_items={_link_items(plan.link_items, output_dir)}",
    )


def _paths(paths, output_dir: Path) -> str:
    """Render replay-relative paths without output-directory-specific absolute text."""
    values = tuple(_relative_path(Path(path), output_dir) for path in paths)
    return ",".join(values) or "none"


def _link_items(items, output_dir: Path) -> str:
    """Render the ordered native link plan with stable path spellings."""
    values = []
    for item in items:
        value = _relative_path(item.value, output_dir) if isinstance(item.value, Path) else str(item.value)
        values.append(f"{item.kind}:{value}")
    return ",".join(values) or "none"


def _relative_path(path: Path, output_dir: Path) -> str:
    """Return an output-relative path or a stable external artifact name."""
    try:
        return path.relative_to(output_dir).as_posix()
    except ValueError:
        return path.name


def _arguments() -> argparse.Namespace:
    """Parse the private maintainer replay command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", choices=("source", "pyi"), required=True)
    parser.add_argument("--unit", choices=tuple(sorted(_REPLAY_UNITS)), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    """Run one clean retained-artifact wrapper-plan replay."""
    args = _arguments()
    report_path = replay_wrapper_plan(
        entry=args.entry,
        unit_name=args.unit,
        output_dir=args.output_dir,
    )
    print(f"Retained wrapper-plan replay: {report_path}")


if __name__ == "__main__":
    main()
