# -*- coding: utf-8 -*-
"""Compiler-derived ABI facts for common C standard-library types.

This module deliberately runs a generated C executable instead of hard-coding
typedef spellings. Names such as ``size_t`` and ``time_t`` are target/compiler
facts, while ``FILE`` is an opaque library handle for wrapper purposes.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
from collections.abc import Sequence

from .preprocessing import PreprocessingConfig, PreprocessingError, validate_macro_name


class CStandardTypeProbeError(ValueError):
    """Raised when a compiler-derived C standard type probe cannot run."""


@dataclass(frozen=True)
class CStandardTypeProbeRecipe:
    """Commands and input flags needed to reproduce one probe result."""

    compiler: str
    compile_argv: list[str]
    run_argv: list[str]
    probe_standard: str = "c11"
    requested_standard: str | None = None
    include_dirs: list[str] | None = None
    defines: list[str] | None = None
    undefs: list[str] | None = None
    compiler_args: list[str] | None = None


@dataclass(frozen=True)
class CStandardTypeProbeReport:
    """JSON-stable ABI facts suitable as input to later C semantic mapping."""

    types: dict[str, dict[str, object]]
    recipe: CStandardTypeProbeRecipe
    source_text: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible report."""
        return asdict(self)


_SIGNED_INTEGER_TYPES = {
    "signed char",
    "short",
    "int",
    "long",
    "long long",
}
_UNSIGNED_INTEGER_TYPES = {
    "unsigned char",
    "unsigned short",
    "unsigned int",
    "unsigned long",
    "unsigned long long",
}
_REAL_TYPES = {"float", "double", "long double"}


def build_c_standard_type_probe_source() -> str:
    """Return the C11 source compiled by :func:`probe_c_standard_types`."""
    return r"""#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>

#define X2PY_BASE_TYPE(value) _Generic((value), \
    char: "char", \
    signed char: "signed char", \
    unsigned char: "unsigned char", \
    short: "short", \
    unsigned short: "unsigned short", \
    int: "int", \
    unsigned int: "unsigned int", \
    long: "long", \
    unsigned long: "unsigned long", \
    long long: "long long", \
    unsigned long long: "unsigned long long", \
    float: "float", \
    double: "double", \
    long double: "long double", \
    default: "other")

#define X2PY_PRINT_ARITHMETIC(name, header, type) \
    printf("\"" name "\":{\"header\":\"" header "\",\"available\":true," \
           "\"kind\":\"arithmetic\",\"underlying_c_type\":\"%s\"," \
           "\"bits\":%zu,\"alignment_bits\":%zu}", \
           X2PY_BASE_TYPE((type)0), \
           sizeof(type) * (size_t)CHAR_BIT, \
           _Alignof(type) * (size_t)CHAR_BIT)

int main(void) {
    printf("{\"types\":{");
    X2PY_PRINT_ARITHMETIC("size_t", "stddef.h", size_t);
    printf(",");
#ifdef UINT32_MAX
    X2PY_PRINT_ARITHMETIC("uint32_t", "stdint.h", uint32_t);
#else
    printf("\"uint32_t\":{\"header\":\"stdint.h\",\"available\":false}");
#endif
    printf(",");
    X2PY_PRINT_ARITHMETIC("time_t", "time.h", time_t);
    printf(",\"FILE\":{\"header\":\"stdio.h\",\"available\":true,"
           "\"kind\":\"opaque_handle\",\"pointer_bits\":%zu,"
           "\"pointer_alignment_bits\":%zu}",
           sizeof(FILE *) * (size_t)CHAR_BIT,
           _Alignof(FILE *) * (size_t)CHAR_BIT);
    printf("}}\n");
    return 0;
}
"""


def _probe_compile_flags(config: PreprocessingConfig) -> list[str]:
    """Carry target-relevant compiler flags into the generated C11 probe."""
    flags = [f"-I{path}" for path in config.include_dirs]
    flags.extend(f"-D{define}" for define in config.defines)
    flags.extend(f"-U{undef}" for undef in config.undefs)
    flags.append("-std=c11")
    flags.extend(config.compiler_args)
    return flags


def _semantic_type_facts(types: dict[str, dict[str, object]]) -> None:
    """Classify arithmetic results for later semantic type conversion."""
    for fact in types.values():
        if not fact.get("available") or fact.get("kind") != "arithmetic":
            continue
        underlying = fact.get("underlying_c_type")
        if underlying in _SIGNED_INTEGER_TYPES:
            fact["kind"] = "integer"
            fact["signed"] = True
            fact["semantic_category"] = "signed_integer"
        elif underlying in _UNSIGNED_INTEGER_TYPES:
            fact["kind"] = "integer"
            fact["signed"] = False
            fact["semantic_category"] = "unsigned_integer"
        elif underlying in _REAL_TYPES:
            fact["kind"] = "real"
            fact["semantic_category"] = "real"
        elif underlying == "char":
            fact["kind"] = "integer"
            fact["semantic_category"] = "integer_implementation_signedness"
        else:
            fact["semantic_category"] = "implementation_defined"


def probe_c_standard_types(
    config: PreprocessingConfig,
    *,
    runner: Sequence[str] | None = None,
) -> CStandardTypeProbeReport:
    """Compile and execute the standard-type probe for one compiler target.

    The default runner executes the produced binary directly, which is
    appropriate for native builds. Cross-compiled targets must provide a
    runner such as an emulator; the command is recorded in the result.
    """
    if not config.compiler:
        raise CStandardTypeProbeError(
            "C standard type probing requires an exact compiler executable"
        )
    if config.compile_commands:
        raise CStandardTypeProbeError(
            "C standard type probing does not consume compile_commands directly; "
            "pass the selected target/include/compiler flags explicitly"
        )

    with tempfile.TemporaryDirectory(prefix="x2py-c-type-probe-") as temp_dir:
        source_path = Path(temp_dir) / "c_standard_type_probe.c"
        executable_path = Path(temp_dir) / (
            "c_standard_type_probe.exe" if os.name == "nt" else "c_standard_type_probe"
        )
        source_text = build_c_standard_type_probe_source()
        source_path.write_text(source_text, encoding="utf-8")

        compile_argv = [
            config.compiler,
            "-x",
            "c",
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
            raise CStandardTypeProbeError(
                f"failed to run C type probe compiler {config.compiler!r}: {exc}"
            ) from exc
        if compiled.returncode != 0:
            command = " ".join(shlex.quote(arg) for arg in compile_argv)
            detail = f": {compiled.stderr.strip()}" if compiled.stderr.strip() else ""
            raise CStandardTypeProbeError(
                f"C standard type probe compilation failed with `{command}`{detail}"
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
            raise CStandardTypeProbeError(
                "failed to execute C standard type probe; provide a compatible "
                f"runner for cross-compiled targets: {exc}"
            ) from exc
        if completed.returncode != 0:
            command = " ".join(shlex.quote(arg) for arg in run_argv)
            detail = f": {completed.stderr.strip()}" if completed.stderr.strip() else ""
            raise CStandardTypeProbeError(
                f"C standard type probe execution failed with `{command}`{detail}"
            )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise CStandardTypeProbeError(
                f"C standard type probe produced invalid JSON: {exc}"
            ) from exc

    types = payload.get("types")
    if not isinstance(types, dict):
        raise CStandardTypeProbeError("C standard type probe output is missing 'types'")
    _semantic_type_facts(types)
    return CStandardTypeProbeReport(
        types=types,
        recipe=CStandardTypeProbeRecipe(
            compiler=config.compiler,
            compile_argv=compile_argv,
            run_argv=run_argv,
            requested_standard=config.std,
            include_dirs=list(config.include_dirs),
            defines=list(config.defines),
            undefs=list(config.undefs),
            compiler_args=list(config.compiler_args),
        ),
        source_text=source_text,
    )


def main(argv: list[str] | None = None) -> int:
    """Run a compiler-derived C standard type probe and write JSON."""
    parser = argparse.ArgumentParser(
        description="Probe C standard-library typedef ABI facts through an exact compiler."
    )
    parser.add_argument("--compiler", required=True, help="Exact native or cross C compiler executable.")
    parser.add_argument("-I", "--include-dir", dest="include_dirs", action="append", default=[])
    parser.add_argument("-D", "--define", dest="defines", action="append", default=[])
    parser.add_argument("-U", "--undef", dest="undefs", action="append", default=[])
    parser.add_argument("--std", help="Original project standard recorded as provenance; the probe itself uses C11.")
    parser.add_argument("--compiler-arg", dest="compiler_args", action="append", default=[])
    parser.add_argument("--runner", dest="runner", action="append", default=[], help="Runner command item for cross targets; repeat for arguments.")
    args = parser.parse_args(argv)
    try:
        for define in args.defines:
            validate_macro_name(define, "--define/-D")
        for undef in args.undefs:
            validate_macro_name(undef, "--undef/-U")
        report = probe_c_standard_types(
            PreprocessingConfig(
                mode="compiler",
                compiler=args.compiler,
                include_dirs=args.include_dirs,
                defines=args.defines,
                undefs=args.undefs,
                std=args.std,
                compiler_args=args.compiler_args,
            ),
            runner=args.runner or None,
        )
    except (PreprocessingError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report.to_dict(), indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through CLI tests.
    raise SystemExit(main())


__all__ = (
    "CStandardTypeProbeError",
    "CStandardTypeProbeRecipe",
    "CStandardTypeProbeReport",
    "build_c_standard_type_probe_source",
    "probe_c_standard_types",
)
