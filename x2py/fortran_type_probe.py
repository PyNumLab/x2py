# -*- coding: utf-8 -*-
"""Compiler-derived Fortran kind expression facts.

Fortran kind values and intrinsics such as ``selected_real_kind`` are
processor/compiler facts.  This module evaluates the exact initialization
expressions requested by the semantic layer through the user-selected Fortran
compiler and flags, then returns values suitable for
``FortranToIRConverter(..., compile_time_values=...)``.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

from .preprocessing import PreprocessingConfig, validate_macro_name


class FortranTypeProbeError(ValueError):
    """Raised when a compiler-derived Fortran type probe cannot run."""


@dataclass(frozen=True)
class FortranTypeProbeRecipe:
    """Commands and input flags needed to reproduce one probe result."""

    compiler: str
    compile_argv: list[str]
    run_argv: list[str]
    expressions: list[str]
    requested_standard: str | None = None
    include_dirs: list[str] | None = None
    defines: list[str] | None = None
    undefs: list[str] | None = None
    compiler_args: list[str] | None = None


@dataclass(frozen=True)
class FortranTypeProbeReport:
    """JSON-stable Fortran kind expression values for semantic conversion."""

    values: dict[str, int]
    recipe: FortranTypeProbeRecipe
    source_text: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible report."""
        return asdict(self)

    def to_compile_time_values(
        self,
        requirements: Iterable[Mapping[str, object]] | None = None,
    ) -> dict[str, int]:
        """Return values keyed for semantic compile-time substitution.

        Exact expression keys are always included.  When semantic requirement
        records are supplied, parameter requirements also add ``symbol -> value``
        mappings, so a parameter such as ``rk = selected_real_kind(12)`` resolves
        both ``selected_real_kind(12)`` and later uses of ``rk``.
        """
        values = dict(self.values)
        if requirements is None:
            return values
        for item in requirements:
            expression = str(item.get("expression") or "").strip()
            symbol = str(item.get("symbol") or "").strip()
            if item.get("code") != "parameter_value" or not expression or not symbol:
                continue
            value = _value_for_expression(self.values, expression)
            if value is not None:
                values[symbol] = value
        return values


_SAFE_EXPRESSION_RE = re.compile(r"^[A-Za-z0-9_+\-*/().,= :]+$")
_TOKEN_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")

_ISO_FORTRAN_ENV_NAMES = {
    "int8",
    "int16",
    "int32",
    "int64",
    "real32",
    "real64",
    "real128",
}
_ISO_C_BINDING_NAMES = {
    "c_bool",
    "c_char",
    "c_double",
    "c_double_complex",
    "c_float",
    "c_float_complex",
    "c_int",
    "c_int16_t",
    "c_int32_t",
    "c_int64_t",
    "c_int8_t",
    "c_long",
    "c_long_double",
    "c_long_double_complex",
    "c_long_long",
    "c_short",
    "c_signed_char",
    "c_size_t",
}


def fortran_type_probe_expressions(
    requirements: Iterable[Mapping[str, object]],
) -> list[str]:
    """Return unique semantic requirement expressions that need probing."""
    expressions: list[str] = []
    seen: set[str] = set()
    for item in requirements:
        expression = str(item.get("expression") or "").strip()
        if not expression:
            continue
        key = expression.lower()
        if key in seen:
            continue
        seen.add(key)
        expressions.append(expression)
    return expressions


def build_fortran_type_probe_source(expressions: Sequence[str]) -> str:
    """Return free-form Fortran source that evaluates integer expressions."""
    unique_expressions = _normalize_expressions(expressions)
    imports = _probe_import_lines(unique_expressions)
    declarations = [
        f"  integer, parameter :: x2py_value_{index} = {expression}"
        for index, expression in enumerate(unique_expressions)
    ]

    lines = [
        "program x2py_fortran_type_probe",
        *imports,
        "  implicit none",
        *declarations,
        "  write(*,'(A)', advance='no') '{\"values\":['",
    ]
    for index, _expression in enumerate(unique_expressions):
        if index:
            lines.append("  write(*,'(A)', advance='no') ','")
        lines.append(f"  write(*,'(I0)', advance='no') x2py_value_{index}")
    lines.extend(
        [
            "  write(*,'(A)') ']}'",
            "end program x2py_fortran_type_probe",
            "",
        ]
    )
    return "\n".join(lines)


def probe_fortran_type_expressions(
    config: PreprocessingConfig,
    expressions: Sequence[str],
    *,
    runner: Sequence[str] | None = None,
) -> FortranTypeProbeReport:
    """Compile and execute a Fortran expression probe for one compiler target.

    The default runner executes the produced binary directly, which matches the
    current native-target assumption.  Cross targets can pass an emulator/runner
    command; the command is recorded in the result.
    """
    if not config.compiler:
        raise FortranTypeProbeError(
            "Fortran type probing requires an exact compiler executable"
        )
    if config.compile_commands:
        raise FortranTypeProbeError(
            "Fortran type probing does not consume compile_commands directly; "
            "pass the selected target/include/compiler flags explicitly"
        )

    unique_expressions = _normalize_expressions(expressions)
    source_text = build_fortran_type_probe_source(unique_expressions)

    with tempfile.TemporaryDirectory(prefix="x2py-fortran-type-probe-") as temp_dir:
        source_path = Path(temp_dir) / "fortran_type_probe.F90"
        executable_path = Path(temp_dir) / (
            "fortran_type_probe.exe" if os.name == "nt" else "fortran_type_probe"
        )
        source_path.write_text(source_text, encoding="utf-8")

        compile_argv = [
            config.compiler,
            *_probe_compile_flags(config),
            str(source_path),
            "-o",
            str(executable_path),
        ]
        try:
            compiled = subprocess.run(
                compile_argv,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            raise FortranTypeProbeError(
                f"failed to run Fortran type probe compiler {config.compiler!r}: {exc}"
            ) from exc
        if compiled.returncode != 0:
            command = " ".join(shlex.quote(arg) for arg in compile_argv)
            detail = f": {compiled.stderr.strip()}" if compiled.stderr.strip() else ""
            raise FortranTypeProbeError(
                f"Fortran type probe compilation failed with `{command}`{detail}"
            )

        run_argv = [*(runner or ()), str(executable_path)]
        try:
            completed = subprocess.run(
                run_argv,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            raise FortranTypeProbeError(
                "failed to execute Fortran type probe; provide a compatible "
                f"runner for cross-compiled targets: {exc}"
            ) from exc
        if completed.returncode != 0:
            command = " ".join(shlex.quote(arg) for arg in run_argv)
            detail = f": {completed.stderr.strip()}" if completed.stderr.strip() else ""
            raise FortranTypeProbeError(
                f"Fortran type probe execution failed with `{command}`{detail}"
            )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise FortranTypeProbeError(
                f"Fortran type probe produced invalid JSON: {exc}"
            ) from exc

    raw_values = payload.get("values")
    if not isinstance(raw_values, list):
        raise FortranTypeProbeError("Fortran type probe output is missing 'values'")
    if len(raw_values) != len(unique_expressions):
        raise FortranTypeProbeError("Fortran type probe output count does not match input expressions")

    values: dict[str, int] = {}
    for expression, value in zip(unique_expressions, raw_values):
        if not isinstance(value, int):
            raise FortranTypeProbeError(
                f"Fortran type probe value for {expression!r} is not an integer"
            )
        values[expression] = value

    return FortranTypeProbeReport(
        values=values,
        recipe=FortranTypeProbeRecipe(
            compiler=config.compiler,
            compile_argv=compile_argv,
            run_argv=run_argv,
            expressions=list(unique_expressions),
            requested_standard=config.std,
            include_dirs=list(config.include_dirs),
            defines=list(config.defines),
            undefs=list(config.undefs),
            compiler_args=list(config.compiler_args),
        ),
        source_text=source_text,
    )


def evaluate_fortran_type_requirements(
    config: PreprocessingConfig,
    requirements: Iterable[Mapping[str, object]],
    *,
    runner: Sequence[str] | None = None,
) -> dict[str, int]:
    """Evaluate collected semantic requirements into compile-time values."""
    requirement_list = list(requirements)
    expressions = fortran_type_probe_expressions(requirement_list)
    if not expressions:
        return {}
    report = probe_fortran_type_expressions(
        config,
        expressions,
        runner=runner,
    )
    return report.to_compile_time_values(requirement_list)


def _normalize_expressions(expressions: Sequence[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for expression in expressions:
        text = str(expression).strip()
        if not text:
            continue
        _validate_expression(text)
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(text)
    return normalized


def _validate_expression(expression: str) -> None:
    if "\n" in expression or "\r" in expression or ";" in expression:
        raise FortranTypeProbeError(
            f"Fortran type probe expression is not a single initialization expression: {expression!r}"
        )
    if _SAFE_EXPRESSION_RE.fullmatch(expression) is None:
        raise FortranTypeProbeError(
            f"Fortran type probe expression contains unsupported characters: {expression!r}"
        )


def _probe_import_lines(expressions: Sequence[str]) -> list[str]:
    tokens = {
        token.lower()
        for expression in expressions
        for token in _TOKEN_RE.findall(expression)
    }
    lines: list[str] = []
    env_names = sorted(tokens & _ISO_FORTRAN_ENV_NAMES)
    c_names = sorted(tokens & _ISO_C_BINDING_NAMES)
    if env_names:
        lines.append(f"  use, intrinsic :: iso_fortran_env, only: {', '.join(env_names)}")
    if c_names:
        lines.append(f"  use, intrinsic :: iso_c_binding, only: {', '.join(c_names)}")
    return lines


def _probe_compile_flags(config: PreprocessingConfig) -> list[str]:
    """Carry target-relevant compiler flags into the generated probe."""
    flags = ["-cpp"]
    flags.extend(f"-I{path}" for path in config.include_dirs)
    flags.extend(f"-D{define}" for define in config.defines)
    flags.extend(f"-U{undef}" for undef in config.undefs)
    if config.std:
        flags.append(f"-std={config.std}")
    flags.extend(config.compiler_args)
    return flags


def _value_for_expression(values: Mapping[str, int], expression: str) -> int | None:
    exact = values.get(expression)
    if exact is not None:
        return exact
    target = expression.strip().lower()
    for key, value in values.items():
        if key.strip().lower() == target:
            return value
    return None


def main(argv: list[str] | None = None) -> int:
    """Run a compiler-derived Fortran type probe and write JSON."""
    parser = argparse.ArgumentParser(
        description="Probe Fortran kind/compile-time expressions through an exact compiler."
    )
    parser.add_argument("--compiler", required=True, help="Exact native or cross Fortran compiler executable.")
    parser.add_argument(
        "--expr",
        "--expression",
        dest="expressions",
        action="append",
        default=[],
        help="Integer initialization expression to evaluate; repeat for multiple expressions.",
    )
    parser.add_argument("-I", "--include-dir", dest="include_dirs", action="append", default=[])
    parser.add_argument("-D", "--define", dest="defines", action="append", default=[])
    parser.add_argument("-U", "--undef", dest="undefs", action="append", default=[])
    parser.add_argument("--std", help="Project Fortran standard passed to the probe compiler.")
    parser.add_argument("--compiler-arg", dest="compiler_args", action="append", default=[])
    parser.add_argument("--runner", dest="runner", action="append", default=[], help="Runner command item for cross targets; repeat for arguments.")
    args = parser.parse_args(argv)
    try:
        for define in args.defines:
            validate_macro_name(define, "--define/-D")
        for undef in args.undefs:
            validate_macro_name(undef, "--undef/-U")
        report = probe_fortran_type_expressions(
            PreprocessingConfig(
                mode="compiler",
                compiler=args.compiler,
                include_dirs=args.include_dirs,
                defines=args.defines,
                undefs=args.undefs,
                std=args.std,
                compiler_args=args.compiler_args,
            ),
            args.expressions,
            runner=args.runner or None,
        )
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(report.to_dict(), indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through CLI tests.
    raise SystemExit(main())


__all__ = (
    "FortranTypeProbeError",
    "FortranTypeProbeRecipe",
    "FortranTypeProbeReport",
    "build_fortran_type_probe_source",
    "evaluate_fortran_type_requirements",
    "fortran_type_probe_expressions",
    "probe_fortran_type_expressions",
)
