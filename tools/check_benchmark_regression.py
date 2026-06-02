#!/usr/bin/env python3
"""Compare benchmark JSON against a reviewed artifact history."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from statistics import median
import sys


DEFAULT_MIN_BASELINES = 10
DEFAULT_THRESHOLD_PERCENT = 15.0


@dataclass(frozen=True)
class BenchmarkComparison:
    name: str
    current_median: float
    baseline_median: float | None
    baseline_count: int
    threshold_percent: float
    min_baselines: int

    @property
    def ready(self) -> bool:
        return self.baseline_count >= self.min_baselines

    @property
    def slowdown_percent(self) -> float | None:
        if self.baseline_median is None:
            return None
        return ((self.current_median / self.baseline_median) - 1.0) * 100.0

    @property
    def regressed(self) -> bool:
        slowdown = self.slowdown_percent
        return self.ready and slowdown is not None and slowdown > self.threshold_percent


def load_benchmark_medians(path: Path) -> dict[str, float]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load benchmark report {path}: {exc}") from exc
    benchmarks = payload.get("benchmarks") if isinstance(payload, dict) else None
    if not isinstance(benchmarks, list):
        raise ValueError(f"benchmark report {path} must contain a benchmarks list")

    medians: dict[str, float] = {}
    for benchmark in benchmarks:
        if not isinstance(benchmark, dict):
            raise ValueError(f"benchmark report {path} contains a non-object benchmark")
        name = benchmark.get("fullname") or benchmark.get("name")
        stats = benchmark.get("stats")
        value = stats.get("median") if isinstance(stats, dict) else None
        if not isinstance(name, str) or not isinstance(value, int | float) or value <= 0:
            raise ValueError(f"benchmark report {path} contains an invalid benchmark entry")
        if name in medians:
            raise ValueError(f"benchmark report {path} contains duplicate benchmark {name!r}")
        medians[name] = float(value)
    return medians


def compare_reports(
    current_path: Path,
    baseline_paths: list[Path],
    *,
    threshold_percent: float = DEFAULT_THRESHOLD_PERCENT,
    min_baselines: int = DEFAULT_MIN_BASELINES,
) -> list[BenchmarkComparison]:
    if threshold_percent < 0:
        raise ValueError("benchmark regression threshold must be non-negative")
    if min_baselines < 1:
        raise ValueError("minimum baseline count must be positive")
    current = load_benchmark_medians(current_path)
    baselines_by_name: dict[str, list[float]] = {}
    for baseline_path in baseline_paths:
        for name, value in load_benchmark_medians(baseline_path).items():
            baselines_by_name.setdefault(name, []).append(value)

    return [
        BenchmarkComparison(
            name=name,
            current_median=value,
            baseline_median=median(baselines) if baselines else None,
            baseline_count=len(baselines),
            threshold_percent=threshold_percent,
            min_baselines=min_baselines,
        )
        for name, value in sorted(current.items())
        for baselines in [baselines_by_name.get(name, [])]
    ]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("current", type=Path, help="Current benchmark JSON report.")
    parser.add_argument("baselines", nargs="*", type=Path, help="Historical benchmark artifact JSON reports.")
    parser.add_argument("--threshold-percent", type=float, default=DEFAULT_THRESHOLD_PERCENT)
    parser.add_argument("--min-baselines", type=int, default=DEFAULT_MIN_BASELINES)
    parser.add_argument("--fail-on-regression", action="store_true")
    parser.add_argument("--require-ready", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(argv or sys.argv[1:]))
    try:
        comparisons = compare_reports(
            args.current,
            args.baselines,
            threshold_percent=args.threshold_percent,
            min_baselines=args.min_baselines,
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    for comparison in comparisons:
        slowdown = comparison.slowdown_percent
        slowdown_label = "no baseline" if slowdown is None else f"{slowdown:+.2f}%"
        readiness = (
            "ready" if comparison.ready else f"needs {comparison.min_baselines - comparison.baseline_count} samples"
        )
        print(
            f"{comparison.name}: current={comparison.current_median:.9f}s "
            f"baseline={comparison.baseline_median or 0.0:.9f}s "
            f"samples={comparison.baseline_count} slowdown={slowdown_label} {readiness}"
        )

    if args.require_ready and any(not comparison.ready for comparison in comparisons):
        return 1
    if args.fail_on_regression and any(comparison.regressed for comparison in comparisons):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
