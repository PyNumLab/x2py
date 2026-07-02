#!/usr/bin/env python3
"""Verify the installed static-analysis toolchain matches the pinned QA versions."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
import sys


EXPECTED_STATIC_ANALYSIS_VERSIONS = {
    "bandit": "1.9.4",
    "radon": "6.0.1",
    "ruff": "0.15.17",
    "vulture": "2.16",
}


def installed_static_analysis_versions() -> dict[str, str | None]:
    installed: dict[str, str | None] = {}
    for package in EXPECTED_STATIC_ANALYSIS_VERSIONS:
        try:
            installed[package] = version(package)
        except PackageNotFoundError:
            installed[package] = None
    return installed


def static_analysis_version_errors(installed: dict[str, str | None]) -> list[str]:
    errors = []
    for package, expected in EXPECTED_STATIC_ANALYSIS_VERSIONS.items():
        actual = installed.get(package)
        if actual is None:
            errors.append(f"{package}: not installed, expected {expected}")
        elif actual != expected:
            errors.append(f"{package}: installed {actual}, expected {expected}")
    return errors


def main() -> int:
    installed = installed_static_analysis_versions()
    errors = static_analysis_version_errors(installed)
    if errors:
        print("Static-analysis tool versions do not match the pinned QA toolchain:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print('Install the pinned toolchain with: python -m pip install -e ".[qa]"', file=sys.stderr)
        return 1

    versions = ", ".join(
        f"{package}=={version}" for package, version in sorted(EXPECTED_STATIC_ANALYSIS_VERSIONS.items())
    )
    print(f"Static-analysis tool versions match: {versions}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
